import pandas as pd
import yaml
import os
from sklearn.model_selection import train_test_split

def preprocess():
    with open("config.yaml","r") as f:
        config = yaml.safe_load(f)
    
    raw_data_path = config['data']['raw_path']
    df = pd.read_csv(raw_data_path)

    df = df.drop(columns= ['instant','dteday','casual','registered'])

    X = df.drop(columns=['cnt'])
    y = df['cnt']

    test_size = config['data']['test_size']
    X_train, X_test , y_train , y_test = train_test_split (X , y , test_size=test_size, random_state=42)

    processed_dir = config['data']['processed_dir']
    os.makedirs(processed_dir, exist_ok=True)

    X_train.to_csv(f"{processed_dir}/X_train.csv" , index=False)
    X_test.to_csv(f"{processed_dir}/X_test.csv" , index=False)
    y_train.to_csv(f"{processed_dir}/y_train.csv" , index=False)
    y_test.to_csv(f"{processed_dir}/y_test.csv" , index=False)

    print(f"success! Processed data saved in this folder '{processed_dir}'")


if __name__ == "__main__":
    preprocess()