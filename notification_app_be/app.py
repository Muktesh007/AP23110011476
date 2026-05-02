from flask import Flask, jsonify
import requests
from logging_middleware.logger import Log
from logging_middleware.config import BASE_URL, TOKEN
from vehicle_maintenance_scheduler.priority import top10

app = Flask(__name__)

headers = {"Authorization": f"Bearer {TOKEN}"}

@app.route("/")
def home():
    return jsonify({
        "message": "Notification API is running",
        "endpoints": {
            "notifications": "/notifications"
        }
    })

@app.route("/notifications")
def notifications():
    try:
        res = requests.get(f"{BASE_URL}/notifications", headers=headers)
        data = res.json()["notifications"]

        result = top10(data)

        Log("backend", "info", "controller", "notifications fetched")

        return jsonify(result)

    except Exception as e:
        Log("backend", "error", "controller", str(e))
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()