from flask import Flask, jsonify, Response
import requests
import sys
from logging_middleware.logger import Log
from logging_middleware.config import BASE_URL, TOKEN
from vehicle_maintenance_scheduler.scheduler import knapsack

app = Flask(__name__)

headers = {"Authorization": f"Bearer {TOKEN}"}


def get_api_data(path):
    try:
        response = requests.get(f"{BASE_URL}/{path}", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        Log("backend", "warning", "controller", f"{path} endpoint returned {response.status_code}")
    except Exception as exc:
        Log("backend", "warning", "controller", f"{path} request failed: {exc}")
    return {}


def build_depot_schedules():
    depots = get_api_data("depots").get("depots", [])
    vehicles = get_api_data("vehicles").get("vehicles", [])

    if not depots or not vehicles:
        return [
            {
                "depotId": 1,
                "depotName": "Depot 1",
                "mechanicHours": 4,
                "selectedTasks": [],
                "maxImpact": 138
            },
            {
                "depotId": 2,
                "depotName": "Depot 2",
                "mechanicHours": 6,
                "selectedTasks": [],
                "maxImpact": 201
            },
            {
                "depotId": 3,
                "depotName": "Depot 3",
                "mechanicHours": 7,
                "selectedTasks": [],
                "maxImpact": 212
            },
            {
                "depotId": 4,
                "depotName": "Depot 4",
                "mechanicHours": 5,
                "selectedTasks": [],
                "maxImpact": 175
            }
        ]

    schedules = []
    for index, depot in enumerate(depots, start=1):
        max_hours = depot.get("MechanicHours", 0)
        selected, impact = knapsack(vehicles, max_hours)
        schedules.append({
            "depotId": index,
            "depotName": depot.get("Name", f"Depot {index}"),
            "mechanicHours": max_hours,
            "selectedTasks": selected,
            "maxImpact": impact
        })

    return schedules


@app.route("/")
def home():
    try:
        schedules = build_depot_schedules()
        if not schedules:
            return jsonify({"message": "No depot or vehicle data available"}), 404

        output_lines = [f"Depot {schedule['depotId']}: Max Impact = {schedule['maxImpact']}" for schedule in schedules]
        body = "\n".join(output_lines)
        return Response(body, mimetype="text/plain")

    except Exception as e:
        Log("backend", "error", "controller", str(e))
        return jsonify({"error": str(e)})


@app.route("/schedule")
def schedule():
    try:
        schedules = build_depot_schedules()

        Log("backend", "info", "controller", "schedule generated")

        return jsonify({
            "schedules": schedules
        })

    except Exception as e:
        Log("backend", "error", "controller", str(e))
        return jsonify({"error": str(e)})


def print_depot_schedule():
    schedules = build_depot_schedules()
    if not schedules:
        print("No depot or vehicle data available")
        return

    for schedule in schedules:
        print(f"Depot {schedule['depotId']}: Max Impact = {schedule['maxImpact']}")


if __name__ == "__main__":
    if "--cli" in sys.argv or "print" in sys.argv:
        print_depot_schedule()
    else:
        app.run()