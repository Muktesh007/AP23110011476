def get_weight(notification_type):
    weights = {
        "Placement": 3,
        "Result": 2,
        "Event": 1
    }
    return weights.get(notification_type, 0)


def top10(notifications):
    # Sort by priority + timestamp
    sorted_notifications = sorted(
        notifications,
        key=lambda x: (get_weight(x["Type"]), x["Timestamp"]),
        reverse=True
    )

    return sorted_notifications[:10]