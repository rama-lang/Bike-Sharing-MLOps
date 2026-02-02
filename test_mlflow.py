import mlflow

# 1. ఎక్స్‌పెరిమెంట్ పేరు సెట్ చేయడం
mlflow.set_experiment("Bike_Sharing_Test")

# 2. రన్ స్టార్ట్ చేయడం
with mlflow.start_run():
    # కొన్ని శాంపిల్ పారామీటర్స్
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 100)
    
    # కొన్ని శాంపిల్ మెట్రిక్స్
    mlflow.log_metric("accuracy", 0.89)
    mlflow.log_metric("rmse", 0.15)
    
    print("Successfully logged test data to MLflow!")