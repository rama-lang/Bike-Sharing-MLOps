import pandas as pd
import sys
import os

def validate_data():
    path = "/opt/airflow/data/bike_sharing_raw.csv"
    
    if not os.path.exists(path):
        print(f"❌ Error: File {path} not found!")
        sys.exit(1)

    df = pd.read_csv(path)
    print(f"✅ Data loaded. Columns: {list(df.columns)}")

    # సింపుల్ పాండాస్ వాలిడేషన్
    errors = []

    # 1. 'cnt' కాలమ్ ఉండాలి మరియు నల్స్ ఉండకూడదు
    if 'cnt' not in df.columns:
        errors.append("Column 'cnt' missing")
    elif df['cnt'].isnull().any():
        errors.append("Null values found in 'cnt'")

    # 2. 'temp' కాలమ్ ఉండాలి
    if 'temp' not in df.columns:
        errors.append("Column 'temp' missing")

    # ఫలితం
    if not errors:
        print("🏆 Data Validation SUCCESSFUL (via Pandas)!")
        sys.exit(0)
    else:
        print(f"❌ Data Validation FAILED: {errors}")
        sys.exit(1)

if __name__ == "__main__":
    validate_data()