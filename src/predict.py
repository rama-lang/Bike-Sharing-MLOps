import pandas as pd
import os
import joblib

def make_prediction(input_data):
    # Model Path Logic
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(BASE_DIR, "models", "bike_model.pkl")

    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        return [0.0]

    model = joblib.load(model_path)

    # Scikit-learn Version Fix
    if hasattr(model, 'monotonic_cst'):
        delattr(model, 'monotonic_cst')

    try:
        # Input Data Formatting
        input_df = pd.DataFrame([input_data]) if isinstance(input_data, dict) else pd.DataFrame(input_data)
        cols = ['season', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed']
        final_df = input_df.reindex(columns=cols, fill_value=0)
        final_df = final_df.apply(pd.to_numeric)
        
        prediction = model.predict(final_df)
        return [float(prediction[0])]
    except Exception as e:
        print(f"❌ Prediction Logic Error: {e}")
        return [0.0]