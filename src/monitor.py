import joblib 
import pandas as pd 
from sklearn.metrics import r2_score 
import os 
import sys

# ఇది చాలా ముఖ్యం
sys.path.append(os.getcwd())

from src.run_pipeline import run_pipeline 

def monitor_and_retrain():
    print("\n🔍 Step 1: Loading model and data for monitoring...")
    
    model_path = 'bike_model.pkl' 
    csv_path = r'C:\MLOPS\data\bike_sharing_raw.csv'

    if not os.path.exists(model_path):
        print("❌ Model not found! Starting training...")
        run_pipeline()
        return

    model = joblib.load(model_path)
    df = pd.read_csv(csv_path)

    # ఫీచర్ ఫిల్టరింగ్
    expected_cols = [
        'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
        'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed'
    ]
    
    X = df[expected_cols] 
    y_true = df['cnt']

    print("📊 Calculating current accuracy...")
    y_pred = model.predict(X)
    current_score = r2_score(y_true, y_pred)
    print(f"✅ Current Accuracy: {current_score:.4f}")

    THRESHOLD = 0.92 
    
    if current_score < THRESHOLD:
        print(f"⚠️ Accuracy is below threshold {THRESHOLD}. Triggering Retraining...")
        run_pipeline()
        print("🚀 Success: Model has been retrained and updated!")
    else:
        print("🟢 Accuracy is good. No action needed.")

if __name__ == "__main__":
    monitor_and_retrain()