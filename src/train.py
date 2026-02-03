import pandas as pd
import yaml
import os
import joblib
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

CONFIG_PATH = "/opt/airflow/src/config.yaml"

def train_model():
    os.chdir("/opt/airflow")
    mlflow.set_experiment("Bike_Sharing_Production")

    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}")
        return

    with open("/opt/airflow/src/config.yaml", "r") as f:
     config = yaml.safe_load(f)
    
    raw_data_path = config['data']['raw_path']
    if os.path.exists(raw_data_path):
        df = pd.read_csv(raw_data_path)
        print(f"Success! Data loaded. Records: {len(df)}")
    else:
        print(f"Error: Data file not found at {os.path.abspath(raw_data_path)}")
    
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
        os.makedirs("/opt/airflow/models", exist_ok=True)
        joblib.dump(model , save_path)

        mlflow.sklearn.log_model(model, "bike_rf_model")

        print(f"Success....Model trained and saved here: {save_path}")
        print(f"MLflow Logged - MSE:{mse}")


if __name__ == "__main__":
    train_model()

