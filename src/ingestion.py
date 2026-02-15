import os
import sys

def load_data():
    # కంటైనర్ లోపల ఫైల్ పాత్ (మనం ఇందాక వెరిఫై చేసింది)
    data_file = "/opt/airflow/data/bike_sharing_raw.csv"
    
    print(f"🔍 Checking for local data file at: {data_file}")

    if os.path.exists(data_file):
        print(f"✅ Found it! Data is already present. Skipping download.")
        # ఒకవేళ ఫైల్ సైజ్ కూడా చూడాలి అనుకుంటే
        size = os.path.getsize(data_file)
        print(f"📊 File size: {size} bytes")
        sys.exit(0) # Success!
    else:
        print(f"❌ Error: File NOT found at {data_file}!")
        sys.exit(1) # Fail!

if __name__ == "__main__":
    load_data()