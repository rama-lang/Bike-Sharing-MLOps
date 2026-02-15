import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from sklearn.model_selection import train_test_split

# ఇక్కడ ఎటువంటి ఇంపోర్ట్స్ (from src... లేదా from run_pipeline...) ఉండకూడదు!

def run_pipeline():
    print("\n🚀 Real Data Training Started...")
    csv_path = r'C:\MLOPS\data\bike_sharing_raw.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ File Not Found at: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)

    # మోడల్ కి కావాల్సిన 12 కాలమ్స్
    expected_cols = [
        'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
        'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed'
    ]

    X = df[expected_cols]
    y = df['cnt']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"🎯 New Model Accuracy: {accuracy:.4f}")

    joblib.dump(model, 'bike_model.pkl')
    print("💾 Model Saved as 'bike_model.pkl'!")

if __name__ == "__main__":
    run_pipeline()