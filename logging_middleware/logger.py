import requests
from .config import TOKEN, BASE_URL

def Log(stack, level, package, message):
    try:
        requests.post(
            f"{BASE_URL}/logs",
            json={
                "stack": stack,
                "level": level,
                "package": package,
                "message": message
            },
            headers={
                "Authorization": f"Bearer {TOKEN}"
            }
        )
    except:
        pass