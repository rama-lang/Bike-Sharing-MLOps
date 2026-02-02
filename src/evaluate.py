import pandas as pd
import yaml
import joblib
from sklearn.metrics import mean_squared_error, r2_score

def evaluate_model():

    with open("config.yaml" , "r") as f:
        config = yaml.safe_load(f)

    processed_dir = config['data']['processed_dir']
    X_test = pd.read_csv(f"{processed_dir}/X_test.csv")
    y_test = pd.read_csv(f"{processed_dir}/y_test.csv")


    model_path = config['model']['save_path']
    model = joblib.load(model_path)


    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test , predictions)


    print("\n---- Model Trport------------" )
    print(f"Mean Sqared error: {mse:.2f}")
    print(f"R2 Score: {r2:.2f}")


if __name__ == "__main__":
    evaluate_model()