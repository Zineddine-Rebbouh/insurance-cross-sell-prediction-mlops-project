from fastapi import FastAPI, Request
import uvicorn
from predict import predict  # Make sure this file and function exist

app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "Welcome to the Insurance Health Cross-Sell Prediction API"}

@app.get('/health')
def health_check():
    return {"status": "healthy"}

@app.post('/predict')
async def predict_endpoint(request: Request):
    try:
        request_data = await request.json()
        print("Received request data:", request_data)

        # If batch input, ensure it is a list
        if isinstance(request_data, dict):
            request_data = [request_data]

        prediction_result = predict(request_data)
        return {"prediction": prediction_result}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
