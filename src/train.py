import pandas as pd
import yaml
import os
import joblib
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# కంటైనర్ లోపల పాత్స్
CONFIG_PATH = "/opt/airflow/src/config.yaml"
MODELS_DIR = "/opt/airflow/models" # ఖచ్చితమైన ఫోల్డర్ అడ్రస్

def train_model():
    # 1. వర్కింగ్ డైరెక్టరీ మార్పు
    os.chdir("/opt/airflow")
    
    # 2. MLflow Tracking URI సెట్ చేయడం (ముఖ్యంగా Docker లో రన్ చేసేటప్పుడు)
    # ఒకవేళ నీకు MLflow కంటైనర్ ఉంటే దాని URL ఇక్కడ ఇవ్వాలి
    mlflow.set_experiment("Bike_Sharing_Production")

    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    
    try:
        # 3. డేటా లోడింగ్
        processed_dir = config['data']['processed_dir']
        # ఇక్కడ కూడా Absolute Path వాడటం మంచిది
        X_train = pd.read_csv(f"/opt/airflow/{processed_dir}/X_train.csv")
        y_train = pd.read_csv(f"/opt/airflow/{processed_dir}/y_train.csv")
        print(f"Data loaded from {processed_dir}")

        with mlflow.start_run(run_name="Random_Forest_Training"):
            print("Model training...........")

            n_estimators = 100
            random_state = 42

            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("random_state", random_state)
            
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
            model.fit(X_train, y_train.values.ravel())

            y_pred = model.predict(X_train)
            mse = mean_squared_error(y_train, y_pred)

            mlflow.log_metric("training_mse", mse)

            # 4. మోడల్ సేవింగ్ - ఇక్కడ జాగ్రత్త!
            os.makedirs(MODELS_DIR, exist_ok=True)
            
            # config లో ఉన్న ఫైల్ పేరు మాత్రమే తీసుకుని MODELS_DIR కి తగిలిద్దాం
            file_name = os.path.basename(config['model']['save_path'])
            final_save_path = os.path.join(MODELS_DIR, file_name)

            joblib.dump(model, final_save_path)
            mlflow.sklearn.log_model(model, "bike_rf_model")

            print(f"✅ Success! Model saved at: {final_save_path}")
            print(f"📊 MLflow Logged - MSE: {mse}")

    except Exception as e:
        print(f"❌ Error occurred during training: {e}")

if __name__ == "__main__":
    train_model()