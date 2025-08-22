import pandas as pd
import numpy as np
import psycopg2
import os
from datetime import datetime
from sklearn import datasets, ensemble
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import ColumnDriftMetric, DatasetMissingValuesMetric
import joblib
import logging
import random
from prefect import task, flow
from prefect.cache_policies import NO_CACHE

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# Constants
SEND_TIMEOUT = 10
rand = random.Random()
REPORTS_DIR = "./app/reports"
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "example",  # Replace with your password
    "host": "localhost",
    "port": "5432"
}

# Create reports directory
os.makedirs(REPORTS_DIR, exist_ok=True)

# Load the model and get feature order
try:
    with open("./app/models/My_Insurance_Model_v1/model.pkl", "rb") as f:
        model = joblib.load(f)
    logging.info("Model loaded successfully.")
    if hasattr(model, 'feature_names_in_'):
        feature_columns = list(model.feature_names_in_)
        logging.info(f"Expected feature order: {feature_columns}")
    else:
        feature_columns = [
            'Gender', 'Age', 'Driving_License', 'Region_Code', 'Previously_Insured',
            'Vehicle_Age', 'Vehicle_Damage', 'Annual_Premium', 'Policy_Sales_Channel',
            'Vintage', 'Annual_Premium_log'
        ]
        logging.warning("Model does not have feature_names_in_. Using hardcoded feature order.")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    raise

# Load reference and current data
try:
    reference_data = pd.read_csv("./data/ref_data.csv")
    raw_data = pd.read_csv("./data/cur_data.csv")
    raw_data = raw_data.drop(columns=["Response"], errors='ignore')  # Drop Response if present
    logging.info(f"Reference data columns: {reference_data.columns.tolist()}")
    logging.info(f"Current data columns: {raw_data.columns.tolist()}")
except Exception as e:
    logging.error(f"Failed to load data: {e}")
    raise

# Verify feature columns
missing_features = [f for f in feature_columns if f not in raw_data.columns or f not in reference_data.columns]
if missing_features:
    logging.error(f"Missing features in data: {missing_features}")
    raise ValueError(f"Missing features in data: {missing_features}")

# Check for missing values in feature columns
numerical_features = ["Age", "Region_Code", "Annual_Premium", "Annual_Premium_log", "Vintage"]
categorical_features = ["Gender", "Driving_License", "Previously_Insured", "Vehicle_Age", "Vehicle_Damage", "Policy_Sales_Channel"]
for col in feature_columns:
    if reference_data[col].isnull().any():
        logging.warning(f"Null values in reference_data['{col}']. Filling with median/mode.")
        if col in numerical_features:
            reference_data[col].fillna(reference_data[col].median(), inplace=True)
        else:
            reference_data[col].fillna(reference_data[col].mode()[0], inplace=True)
    if raw_data[col].isnull().any():
        logging.warning(f"Null values in raw_data['{col}']. Filling with median/mode.")
        if col in numerical_features:
            raw_data[col].fillna(raw_data[col].median(), inplace=True)
        else:
            raw_data[col].fillna(raw_data[col].mode()[0], inplace=True)

# Verify Response in reference_data
if 'Response' not in reference_data.columns:
    logging.error("Response column missing in reference_data")
    raise ValueError("Response column missing in reference_data")
if reference_data['Response'].isnull().any():
    logging.warning("Null values in reference_data['Response']. Filling with 0.")
    reference_data['Response'].fillna(0, inplace=True)

# Define column mapping for Evidently
column_mapping = ColumnMapping(
    prediction="prediction_proba",
    numerical_features=[f for f in numerical_features if f in feature_columns],
    categorical_features=[f for f in categorical_features if f in feature_columns],
    target=None  # No target for current data
)

# Generate predictions for both reference and current data
try:
    # Reference data predictions
    reference_data["prediction_proba"] = model.predict_proba(reference_data[feature_columns])[:, 1]
    reference_data["prediction"] = (reference_data["prediction_proba"] >= 0.5).astype(int)
    # Current data predictions
    raw_data["prediction_proba"] = model.predict_proba(raw_data[feature_columns])[:, 1]
    raw_data["prediction"] = (raw_data["prediction_proba"] >= 0.5).astype(int)
    
    # Validate prediction_proba
    if reference_data["prediction_proba"].isnull().any() or reference_data["prediction"].isnull().any():
        logging.warning("Null values in reference_data predictions. Filling with 0.")
        reference_data["prediction_proba"].fillna(0, inplace=True)
        reference_data["prediction"].fillna(0, inplace=True)
    if raw_data["prediction_proba"].isnull().any() or raw_data["prediction"].isnull().any():
        logging.warning("Null values in raw_data predictions. Filling with 0.")
        raw_data["prediction_proba"].fillna(0, inplace=True)
        raw_data["prediction"].fillna(0, inplace=True)
    
    # Check for constant prediction_proba
    if reference_data["prediction_proba"].nunique() <= 1:
        logging.warning("reference_data['prediction_proba'] has constant values, which may cause drift metric failure.")
    if raw_data["prediction_proba"].nunique() <= 1:
        logging.warning("raw_data['prediction_proba'] has constant values, which may cause drift metric failure.")
    
    logging.info("Predictions generated for both reference and current data.")
    logging.info(f"Reference data shape: {reference_data.shape}")
    logging.info(f"Current data shape: {raw_data.shape}")
    logging.info(f"Null values in reference prediction_proba: {reference_data['prediction_proba'].isnull().sum()}")
    logging.info(f"Null values in current prediction_proba: {raw_data['prediction_proba'].isnull().sum()}")
except Exception as e:
    logging.error(f"Failed to generate predictions: {e}")
    raise

# Initialize Evidently report
report = Report(metrics=[
    DataDriftPreset(),
    ColumnDriftMetric(column_name="prediction_proba"),
    DatasetMissingValuesMetric()
])

# Database table creation query
create_table_query = """
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    drift_score FLOAT,
    number_of_drifted_columns INT,
    share_of_missing_values FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

@task
def connect_db():
    """
    Connect to the PostgreSQL database and verify table schema.
    
    Returns:
        connection: Database connection object
        cursor: Database cursor object
    """
    try:
        logging.info("Connecting to the PostgreSQL database...")
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create table if it doesn't exist
        cursor.execute(create_table_query)
        connection.commit()
        
        # Verify table schema
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'metrics';
        """)
        columns = [row[0] for row in cursor.fetchall()]
        expected_columns = ['id', 'metric_name', 'drift_score', 
                          'number_of_drifted_columns', 'share_of_missing_values', 'created_at']
        missing_columns = [col for col in expected_columns if col not in columns]
        if missing_columns:
            logging.warning(f"Metrics table missing columns: {missing_columns}. Attempting to add...")
            for col in missing_columns:
                if col == 'drift_score':
                    cursor.execute("ALTER TABLE metrics ADD COLUMN drift_score FLOAT;")
                elif col == 'number_of_drifted_columns':
                    cursor.execute("ALTER TABLE metrics ADD COLUMN number_of_drifted_columns INT;")
                elif col == 'share_of_missing_values':
                    cursor.execute("ALTER TABLE metrics ADD COLUMN share_of_missing_values FLOAT;")
                elif col == 'metric_name':
                    cursor.execute("ALTER TABLE metrics ADD COLUMN metric_name VARCHAR(255) NOT NULL;")
                elif col == 'created_at':
                    cursor.execute("ALTER TABLE metrics ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            connection.commit()
        
        logging.info("Database connection established and metrics table verified.")
        return connection, cursor
    except Exception as e:
        logging.error(f"Failed to connect to the database or verify schema: {e}")
        raise

@task(cache_policy=NO_CACHE)
def calculate_metrics_postgresql(connection, cursor, curr, i):
    """
    Calculate metrics and save to PostgreSQL.
    
    Parameters:
        connection: PostgreSQL connection object
        cursor: PostgreSQL cursor object
        curr (DataFrame): Current data for metric calculation
        i (int): Batch index
    
    Returns:
        None
    """
    try:
        logging.info(f"Calculating metrics for batch {i}...")
        # Generate predictions for the batch
        curr["prediction_proba"] = model.predict_proba(curr[feature_columns])[:, 1]
        curr["prediction"] = (curr["prediction_proba"] >= 0.5).astype(int)
        if curr["prediction_proba"].isnull().any() or curr["prediction"].isnull().any():
            logging.warning("Null values in batch predictions. Filling with 0.")
            curr["prediction_proba"].fillna(0, inplace=True)
            curr["prediction"].fillna(0, inplace=True)
        
        # Run Evidently report
        report.run(reference_data=reference_data, current_data=curr, column_mapping=column_mapping)
        
        # Extract metrics
        results = report.as_dict()
        logging.info(f"Evidently report metrics for batch {i}: {results['metrics']}")  # Debug metric structure
        
        # Initialize metrics with defaults
        drift_score = 0.0
        number_of_drifted_columns = 0
        share_of_missing_values = 0.0
        
        # Extract important metrics dynamically
        for metric in results["metrics"]:
            if metric["metric"] == "ColumnDriftMetric" and metric["result"].get("column_name") == "prediction_proba":
                drift_score = metric["result"].get("drift_score", 0.0)
            elif metric["metric"] == "DataDriftTable":
                number_of_drifted_columns = metric["result"].get("number_of_drifted_columns", 0)
            elif metric["metric"] == "DatasetMissingValuesMetric":
                share_of_missing_values = metric["result"]["current"].get("share_of_missing_values", 0.0)
        
        # Log extracted metrics
        logging.info(f"Metrics for batch {i}: drift_score={drift_score}, "
                     f"number_of_drifted_columns={number_of_drifted_columns}, "
                     f"share_of_missing_values={share_of_missing_values}")
        
        # Save metrics to PostgreSQL
        cursor.execute(
            """
            INSERT INTO metrics (
                metric_name, drift_score, number_of_drifted_columns, 
                share_of_missing_values
            ) VALUES (%s, %s, %s, %s)
            """,
            (
                "batch_monitoring",
                drift_score,
                number_of_drifted_columns,
                share_of_missing_values
            )
        )
        connection.commit()
        logging.info(f"Metrics saved to PostgreSQL for batch {i}")
        
        # Save Evidently report as HTML
        report_path = os.path.join(REPORTS_DIR, f"batch_monitoring_report_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        report.save_html(report_path)
        logging.info(f"Evidently report saved to {report_path}")
        
    except Exception as e:
        logging.error(f"Failed to calculate metrics for batch {i}: {e}")
        raise

@flow
def batch_monitoring_flow():
    """
    Batch monitoring flow to process current data, calculate metrics, and save to PostgreSQL.
    """
    try:
        connection, cursor = connect_db()
        batch_size = 10000
        num_batches = len(raw_data) // batch_size + (1 if len(raw_data) % batch_size else 0)
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(raw_data))
            curr_batch = raw_data.iloc[start_idx:end_idx].copy()
            calculate_metrics_postgresql(connection, cursor, curr_batch, i)
        
        logging.info("Batch monitoring completed successfully.")
        
    except Exception as e:
        logging.error(f"Batch monitoring flow failed: {e}")
        raise
    finally:
        if "connection" in locals() and connection:
            cursor.close()
            connection.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    batch_monitoring_flow()