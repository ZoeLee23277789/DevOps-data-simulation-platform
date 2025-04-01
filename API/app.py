from flask import Flask, request, jsonify, render_template
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge
from pymongo import MongoClient
from bson import json_util
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
# 自訂 Prometheus 指標
temperature_metric = Gauge('machine_temperature', 'Machine temperature in °C', ['machine_id'])
pressure_metric = Gauge('machine_pressure', 'Machine pressure in bar', ['machine_id'])

# 使用 PrometheusMetrics 自動監控所有請求，並建立 /metrics 端點
metrics = PrometheusMetrics(app)

# MongoDB 連線
MONGO_URI = "mongodb://mongo:27017/"
client = MongoClient(MONGO_URI)
db = client["sensor_db"]
collection = db["sensor_data"]
alert_collection = db["alert_log"]

#==================================================================================================
# 寫入資料
@app.route("/log_data", methods=["POST"])
def log_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
    

    # 👉 更新 Prometheus 指標
    temperature_metric.labels(machine_id=data["machine_id"]).set(data["temperature"])
    pressure_metric.labels(machine_id=data["machine_id"]).set(data["pressure"])
   
    if data["temperature"] > 90 or data["pressure"] > 2.2:
        alert_collection.insert_one({
            "machine_id": data["machine_id"],
            "issue": "High temperature/pressure",
            "data": data
        })
    result = collection.insert_one(data)
    return jsonify({
        "status": "success",
        "inserted_id": str(result.inserted_id)
    }), 200

#==================================================================================================
# 取得最新的 10 筆資料
@app.route("/get_data", methods=["GET"])
def get_data():
    all_data = list(collection.find().sort("timestamp", -1).limit(10))
    return json_util.dumps(all_data), 200

#==================================================================================================
# 取得最新一筆資料
@app.route("/latest_data", methods=["GET"])
def latest_data():
    latest_entry = collection.find_one(sort=[("timestamp", -1)])
    if latest_entry:
        latest_entry["_id"] = str(latest_entry["_id"])
        return jsonify({"status": "success", "latest": latest_entry}), 200
    else:
        return jsonify({"status": "no data"}), 404

#==================================================================================================
@app.route("/get_latest_per_machine", methods=["GET"])
def get_latest_per_machine():
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$machine_id",
            "latest_record": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$latest_record"}}
    ]
    data = list(collection.aggregate(pipeline))
    return json_util.dumps(data), 200

#================================================================================================== 
# 取得指定機台最新 10 筆資料
@app.route("/get_machine_data", methods=["GET"])
def get_machine_data():
    machine_id = request.args.get("machine_id")
    if not machine_id:
        return jsonify({"error": "Missing machine_id"}), 400

    data = list(collection.find({"machine_id": machine_id}).sort("timestamp", -1).limit(10))
    return json_util.dumps(data), 200

#==================================================================================================
# 取得最新的告警記錄
@app.route("/alerts", methods=["GET"])
def get_alerts():
    alerts = list(alert_collection.find().sort("data.timestamp", -1).limit(10))
    return json_util.dumps(alerts), 200

#==================================================================================================
# 清除所有資料
@app.route("/clear_data", methods=["POST"])
def clear_data():
    collection.delete_many({})
    alert_collection.delete_many({})
    return jsonify({"status": "all data cleared"}), 200

#==================================================================================================
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
