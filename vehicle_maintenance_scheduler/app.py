from flask import Flask, jsonify
import requests
from logging_middleware.logger import Log
from logging_middleware.config import BASE_URL, TOKEN
from vehicle_maintenance_scheduler.scheduler import knapsack

app = Flask(__name__)

headers = {"Authorization": f"Bearer {TOKEN}"}

@app.route("/schedule")   
def schedule():
    try:
        depots = requests.get(f"{BASE_URL}/depots", headers=headers).json()
        vehicles = requests.get(f"{BASE_URL}/vehicles", headers=headers).json()

        max_hours = depots["depots"][0]["MechanicHours"]
        tasks = vehicles["vehicles"]

        selected, impact = knapsack(tasks, max_hours)

        Log("backend", "info", "controller", "schedule generated")

        return jsonify({
            "selectedTasks": selected,
            "totalImpact": impact
        })

    except Exception as e:
        Log("backend", "error", "controller", str(e))
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()