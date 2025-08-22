import pickle
import pandas as pd
import os

# Load the model
model_path = "C:\\Users\\mkrym\\OneDrive\\Desktop\\Machine learning\\MLops\\project-1\\app\\models\\My_Insurance_Model\\model.pkl"
print(f"Loading model from: {model_path}")
model = None

try:
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
        print("Model loaded successfully.")
except FileNotFoundError:
    print(f"❌ Model file not found at: {os.path.abspath(model_path)}")
except Exception as e:
    print(f"❌ Error loading model: {e}")

def predict(input_data):
    if model is None:
        raise ValueError("🚨 Model is not loaded. Cannot perform prediction.")
    
    df = pd.DataFrame(input_data)

    # Optional: drop target if exists
    df = df.drop(columns=["Response"], errors="ignore")

    try:
        prediction = model.predict(df)
        if hasattr(prediction, "tolist"):
            prediction = prediction.tolist()
        return prediction
    except Exception as e:
        return f"Prediction failed: {e}"
