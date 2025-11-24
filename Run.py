"""
run.py - Client แบบไฟล์เดียว
รวม TPSClip, HelpMe+ backend, API, module manager, heartbeat
Client ID = apiSC
"""

import time
import threading
import requests
from flask import Flask, jsonify

# -------------------------
# Common Helpers
# -------------------------
class Common:
    @staticmethod
    def log(message):
        print(f"[LOG] {message}")

    @staticmethod
    def api_request(url, method="GET", data=None, headers=None):
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers)
            else:
                resp = requests.post(url, json=data, headers=headers)
            return resp.json()
        except Exception as e:
            Common.log(f"API request error: {e}")
            return None

# -------------------------
# TPSClip Module
# -------------------------
class TPSClipClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        Common.log("TPSClipClient initialized")

    def connect(self):
        if self.api_key:
            Common.log(f"Connecting TPSClip API with key: {self.api_key}")
        else:
            Common.log("No API key, demo mode")
        return True

    def run(self):
        Common.log("TPSClip module running...")
        time.sleep(2)
        Common.log("TPSClip task complete.")

# -------------------------
# HelpMe+ Backend
# -------------------------
app = Flask(__name__)
tasks_status = []

@app.route("/")
def index():
    return jsonify(tasks_status)

@app.route("/log_task/<task>/<status>")
def log_task(task, status):
    tasks_status.append({"task": task, "status": status})
    return jsonify({"success": True})

def run_web():
    app.run(host="0.0.0.0", port=5000)

# -------------------------
# Module Manager
# -------------------------
class ModuleManager:
    def __init__(self):
        self.modules = []

    def add_module(self, module):
        self.modules.append(module)
        Common.log(f"Module '{module.__class__.__name__}' added.")

    def run_all(self):
        for m in self.modules:
            if hasattr(m, "run"):
                m.run()

# -------------------------
# Server Client
# -------------------------
SERVER_URL = "http://YOUR_SERVER_ADDRESS:8000"

class ServerClient:
    def __init__(self, client_id="apiSC"):
        self.client_id = client_id
        self.running = True

    def send_heartbeat(self):
        while self.running:
            try:
                requests.post(f"{SERVER_URL}/heartbeat", json={"client_id": self.client_id})
                Common.log("Heartbeat sent")
            except Exception as e:
                Common.log(f"Heartbeat error: {e}")
            time.sleep(10)

    def fetch_task(self):
        try:
            resp = requests.get(f"{SERVER_URL}/get_task?client_id={self.client_id}")
            if resp.status_code == 200 and resp.json().get("task"):
                return resp.json()["task"]
        except Exception as e:
            Common.log(f"Fetch task error: {e}")
        return None

# -------------------------
# Auto-Updater (optional)
# -------------------------
def auto_update():
    import subprocess, os
    while True:
        Common.log("Checking for updates...")
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"])
            subprocess.run(["git", "remote", "add", "origin", "https://github.com/YOUR_USERNAME/apiSC.git"])
        subprocess.run(["git", "pull", "origin", "main"])
        subprocess.run(["pip", "install", "-r", "requirements.txt"])
        Common.log("Update complete. Restarting...")
        time.sleep(3600)  # เช็คทุกชั่วโมง

# -------------------------
# Main Program
# -------------------------
def main():
    Common.log("run.py starting...")

    # TPSClip client
    tps_client = TPSClipClient(api_key="YOUR_TPSCLIP_KEY")
    tps_client.connect()

    # Module manager
    manager = ModuleManager()
    manager.add_module(tps_client)

    # Server client
    server_client = ServerClient(client_id="apiSC")
    threading.Thread(target=server_client.send_heartbeat, daemon=True).start()

    # Web backend
    threading.Thread(target=run_web, daemon=True).start()

    # Auto-updater (optional)
    threading.Thread(target=auto_update, daemon=True).start()

    # Main loop
    while True:
        task = server_client.fetch_task()
        if task:
            Common.log(f"Running server task: {task}")
            manager.run_all()
            requests.get(f"http://127.0.0.1:5000/log_task/{task}/completed")
        else:
            manager.run_all()
        time.sleep(5)

if __name__ == "__main__":
    main()
