"""Send random traffic to TaskTracker so Grafana has something to draw.

Usage:
    python scripts/traffic.py                         # http://localhost:8000
    python scripts/traffic.py http://localhost:8001   # another address

Press Ctrl+C to stop. Uses only the Python standard library.
"""
import json
import random
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"

# (method, path, weight)
ACTIONS = [
    ("GET", "/", 40),
    ("GET", "/tasks", 20),
    ("POST", "/tasks", 15),
    ("GET", "/slow", 15),
    ("GET", "/error", 10),
]


def send(method, path):
    data = None
    headers = {}
    if method == "POST":
        data = json.dumps({"title": f"Task {random.randint(1, 999)}"}).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as err:
        return err.code


def main():
    paths = [(m, p) for m, p, w in ACTIONS for _ in range(w)]
    print(f"Sending traffic to {BASE} - press Ctrl+C to stop")
    count = 0
    try:
        while True:
            method, path = random.choice(paths)
            try:
                status = send(method, path)
            except urllib.error.URLError as err:
                print(f"Cannot reach {BASE}: {err.reason}")
                time.sleep(2)
                continue
            count += 1
            if count % 20 == 0:
                print(f"{count} requests sent (last: {method} {path} -> {status})")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print(f"\nStopped after {count} requests.")


if __name__ == "__main__":
    main()
