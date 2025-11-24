"""
comSC - Client สำหรับเชื่อมต่อ server และ Scanzaclip
ไฟล์เดียวรันได้ต่อเนื่อง 24/7
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

# -------------------------
# Scanzaclip Module
# -------------------------
class ScanzaclipClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        Common.log("ScanzaclipClient initialized")

    def connect(self):
        if self.api_key:
            Common.log(f"Connecting to Scanzaclip with API Key: {self.api_key}")
        else:
            Common.log("No API Key provided. Running in demo mode.")
        return True

    def run(self):
        Common.log("Scanzaclip module running...")
        time.sleep(2)
        Common.log("Scanzaclip task complete.")

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
SERVER_URL = "http://YOUR_SERVER_ADDRESS:8000"  # เปลี่ยนเป็น server จริงของคุณ

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
            response = requests.get(f"{SERVER_URL}/get_task?client_id={self.client_id}")
            if response.status_code == 200 and response.json().get("task"):
                return response.json()["task"]
        except Exception as e:
            Common.log(f"Fetch task error: {e}")
        return None

# -------------------------
# Main Program
# -------------------------
def main():
    Common.log("comSC starting...")

    # สร้าง client Scanzaclip
    sc_client = ScanzaclipClient(api_key="YOUR_API_KEY")
    sc_client.connect()

    # สร้าง module manager และเพิ่มโมดูล
    manager = ModuleManager()
    manager.add_module(sc_client)

    # สร้าง server client (client ID = comSC)
    server_client = ServerClient(client_id="comSC")
    threading.Thread(target=server_client.send_heartbeat, daemon=True).start()

    # รัน main loop
    while True:
        task = server_client.fetch_task()
        if task:
            Common.log(f"Running server task: {task}")
            # ตัวอย่างรัน task (สามารถ map เป็น module ได้)
            time.sleep(2)
            Common.log("Server task completed")
        else:
            manager.run_all()
        time.sleep(5)

# -------------------------
# Run Program
# -------------------------
if __name__ == "__main__":
    main()
