import joblib
import pandas as pd

# మోడల్ ని లోడ్ చేస్తున్నాం
model = joblib.load("models/bike_model.pkl")

# టెస్ట్ డేటా ని లోడ్ చేస్తున్నాం
X_test = pd.read_csv("data/processed/X_test.csv")

# మొదటి 5 ప్రిడిక్షన్స్ చూద్దాం
predictions = model.predict(X_test.head())

print("🚀 Model Predictions for first 5 rows:")
print(predictions)