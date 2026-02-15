import requests
import time

# నీ API ఎండ్‌పాయింట్
URL = "http://localhost:8000/predict"

def run_stress_test(total_requests=50):
    print(f"🚀 Testing with URL: {URL}")
    print(f"🔥 Sending high raw_value (999) to hit the Red Line!")
    
    for i in range(total_requests):
        # ఇక్కడ మనం కావాలని చాలా తప్పుడు వాల్యూ (999) పంపుతున్నాం
        payload = {
            "season": 1,
            "hr": 10,
            "temp": 0.5,
            "hum": 0.5,
            "raw_value": 999.0  
        }
        
        try:
            response = requests.post(URL, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {i+1}: Success! Spike Sent.")
            else:
                print(f"❌ {i+1}: Failed with {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            break
            
        time.sleep(0.3) # గ్రాఫ్ మెల్లగా పైకి వెళ్లడం చూడటానికి చిన్న గ్యాప్

if __name__ == "__main__":
    run_stress_test()