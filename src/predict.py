import pandas as pd
import os
import mlflow
import mlflow.sklearn

def make_prediction(input_data):
    # 1. MLflow అడ్రస్ సెట్ చేయడం
    if os.path.exists("/opt/airflow"):
        ml_uri = "http://172.18.0.1:5000" 
    else:
        ml_uri = "http://localhost:5000"
        
    mlflow.set_tracking_uri(ml_uri)

    # 2. Model URI - ఇక్కడ మనం Alias (@champion) వాడుతున్నాం
    model_uri = "models:/Bike_Sharing_Model@champion"
    
    try:
        # 3. మోడల్ లోడ్ చేయడం (Registry నుండి నేరుగా!)
        # ఇక్కడ joblib.load అవసరం లేదు, MLflow చూసుకుంటుంది
        print(f"📡 Loading model from Registry: {model_uri}")
        model = mlflow.sklearn.load_model(model_uri)

        # 4. కాలమ్స్ ఆర్డర్ సెట్ చేయడం
        if hasattr(model, 'feature_names_in_'):
            input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)

        # 5. ప్రెడిక్షన్
        prediction = model.predict(input_data)
        
        # 6. MLflow లోకి లాగ్ చేయడం
        mlflow.set_experiment("Bike_Sharing_Production") 
        with mlflow.start_run(run_name="Final_Inference_Check"):
            mlflow.log_metric("predicted_value", float(prediction[0]))
            print(f"🚀 MLflow Log Success! Value: {prediction[0]}")
            
        return prediction

    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        raise e