"""
apiSC - Client แบบไฟล์เดียว
เชื่อมต่อ API ทั้งหมด, TPSClip และ HelpMe+
Client ID: apiSC
"""

import time
import threading
import requests

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
            Common.log(f"Connecting to TPSClip API with key: {self.api_key}")
        else:
            Common.log("No API key provided. Running demo mode")
        return True

    def run(self):
        Common.log("TPSClip module running...")
        # ตัวอย่าง task
        time.sleep(2)
        Common.log("TPSClip task complete.")

# -------------------------
# HelpMe+ Admin Module
# -------------------------
class HelpMeAdmin:
    def __init__(self, admin_key=None):
        self.admin_key = admin_key
        Common.log("HelpMeAdmin initialized")

    def connect(self):
        Common.log("Connecting to HelpMe+ backend...")
        return True

    def log_task(self, task, status):
        Common.log(f"[HelpMe+] Task: {task}, Status: {status}")

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
        Common.log("Running all modules...")
        for m in self.modules:
            if hasattr(m, "run"):
                m.run()
        Common.log("All modules completed.")

# -------------------------
# Server Client
# -------------------------
SERVER_URL = "http://YOUR_SERVER_ADDRESS:8000"

class ServerClient:
    def __init__(self, client_id):
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
# Main Program
# -------------------------
def main():
    Common.log("apiSC starting...")

    # สร้าง TPSClip client
    tps_client = TPSClipClient(api_key="YOUR_TPSCLIP_KEY")
    tps_client.connect()

    # สร้าง HelpMe+ admin
    help_admin = HelpMeAdmin(admin_key="YOUR_ADMIN_KEY")
    help_admin.connect()

    # Module manager
    manager = ModuleManager()
    manager.add_module(tps_client)

    # Server client (Client ID = apiSC)
    server_client = ServerClient(client_id="apiSC")
    threading.Thread(target=server_client.send_heartbeat, daemon=True).start()

    # Main loop
    while True:
        task = server_client.fetch_task()
        if task:
            Common.log(f"Running server task: {task}")
            manager.run_all()  # สามารถ map task เป็น module ได้
            help_admin.log_task(task, "completed")
        else:
            manager.run_all()
        time.sleep(5)

if __name__ == "__main__":
    main()
