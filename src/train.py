import pandas as pd
import yaml
import os
import joblib
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


def train_model():

    mlflow.set_experiment("Bike_Sharing_Production")

    with open("config.yaml" , "r") as f:
        config = yaml.safe_load(f)
    
    processed_dir = config['data']['processed_dir']
    X_train = pd.read_csv(f"{processed_dir}/X_train.csv")
    y_train = pd.read_csv(f"{processed_dir}/y_train.csv")

    with mlflow.start_run(run_name="Random_Forest_Training"):
        print("Model training...........")

        n_estimators = 100
        random_state = 42

        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("random_state", random_state)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train.values.ravel())

        y_pred = model.predict(X_train)
        mse = mean_squared_error(y_train, y_pred)

        mlflow.log_metric("training_mse" , mse)
        save_path = config['model']['save_path']
        os.makedirs('models', exist_ok=True)
        joblib.dump(model , save_path)

        mlflow.sklearn.log_model(model, "bike_rf_model")

        print(f"Success....Model trained and saved here: {save_path}")
        print(f"MLflow Logged - MSE:{mse}")


if __name__ == "__main__":
    train_model()

