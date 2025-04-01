from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from pymongo import MongoClient

def export_csv():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["sensor_db"]
    collection = db["sensor_data"]

    now = datetime.now()
    output_path = f"/opt/airflow/exported_reports/{now.strftime('%Y-%m-%d_%H%M')}.csv"

    cursor = collection.find({
        "timestamp": {
            "$gte": datetime(now.year, now.month, now.day, now.hour)
        }
    })

    df = pd.DataFrame(list(cursor))
    df.to_csv(output_path, index=False)

default_args = {
    'start_date': datetime(2025, 4, 1),
}

with DAG(
    'export_sensor_data_hourly', 
    default_args=default_args, 
    schedule_interval='@hourly', 
    catchup=False
) as dag:
    
    export = PythonOperator(
        task_id='export_sensor_csv',
        python_callable=export_csv
    )
