"""TaskTracker - a tiny Flask API used to learn DevOps tools.

Endpoints
  GET    /            greeting, version and which container answered
  GET    /health      health check (used by Docker and Kubernetes)
  GET    /tasks       list tasks
  POST   /tasks       create a task  {"title": "Learn Docker"}
  DELETE /tasks/<id>  delete a task
  GET    /slow        slow response (for latency graphs)
  GET    /error       always fails with HTTP 500 (for error graphs)
  GET    /metrics     Prometheus metrics
"""
import os
import random
import socket
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")
APP_GREETING = os.getenv("APP_GREETING", "Hello from TaskTracker!")

# Tasks live in memory. When the container restarts, they are gone.
tasks = []
next_id = 1

# ---------- Prometheus metrics ----------
REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)
TASKS_GAUGE = Gauge("app_tasks_total", "Number of tasks currently stored")


@app.before_request
def start_timer():
    g.start_time = time.time()


@app.after_request
def record_metrics(response):
    endpoint = request.url_rule.rule if request.url_rule else "unknown"
    if endpoint != "/metrics":
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        REQUEST_LATENCY.labels(endpoint).observe(time.time() - g.start_time)
    return response


# ---------- Routes ----------
@app.route("/")
def index():
    return jsonify(
        message=APP_GREETING,
        version=APP_VERSION,
        served_by=socket.gethostname(),
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(error="'title' is required"), 400
    task = {"id": next_id, "title": title, "done": False}
    next_id += 1
    tasks.append(task)
    TASKS_GAUGE.set(len(tasks))
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            TASKS_GAUGE.set(len(tasks))
            return "", 204
    return jsonify(error="task not found"), 404


@app.route("/slow")
def slow():
    time.sleep(random.uniform(0.2, 1.5))
    return jsonify(message="That was slow on purpose")


@app.route("/error")
def error():
    return jsonify(error="Simulated failure"), 500


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
