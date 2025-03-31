import time
import random
import requests
from datetime import datetime, timedelta
from threading import Thread

API_URL = "http://flask_api:5000/log_data"

# 設定要模擬的機台清單
MACHINE_IDS = ["TSMC-M1", "TSMC-M2", "TSMC-M3", "TSMC-M4", "TSMC-M5"]

def generate_sensor_data(machine_id):
    """產生單台機器的感測器數據"""
    return {
        "machine_id": machine_id,
        "temperature": round(random.uniform(60, 100), 2),
        "pressure": round(random.uniform(1.0, 2.5), 2),
        "timestamp": (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    }

def simulate_device(machine_id):
    """模擬單台設備定期送出資料"""
    while True:
        data = generate_sensor_data(machine_id)
        try:
            response = requests.post(API_URL, json=data)
            print(f"✅ {machine_id} Sent: {data} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {machine_id} Failed to send data: {e}")
        time.sleep(5)

def main():
    threads = []
    for machine_id in MACHINE_IDS:
        t = Thread(target=simulate_device, args=(machine_id,))
        t.start()
        threads.append(t)

    # 保持主線程運行
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
