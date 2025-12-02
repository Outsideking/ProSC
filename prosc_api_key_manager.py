# prosc_api_key_manager.py
# ระบบจัดการ API Key สำหรับ PROSC พร้อมระบบต่ออายุอัตโนมัติและการหักเงิน TPS Global

import os
import json
from getpass import getpass
from datetime import datetime, timedelta
import requests

# --- Mock TPS Global payment module ---
def tps_global_deduct(amount_usd, service_name):
    print(f"Deducting ${amount_usd} for {service_name} from TPS Global...")
    return True

# --- Mock API key registration function ---
def get_api_key_from_service(service_name):
    return f'{service_name.upper()}_GENERATED_KEY'

class ProscAPIKeyManager:
    def __init__(self, storage_file="prosc_api_keys.json"):
        self.storage_file = storage_file
        if not os.path.exists(storage_file):
            with open(storage_file, "w") as f:
                json.dump({}, f)

    def add_key(self, service_name, api_key=None, paid=False, amount_usd=0, billing_cycle="Annual"):
        if paid:
            if not tps_global_deduct(amount_usd, service_name):
                print(f"Payment failed. Cannot subscribe to {service_name}.")
                return
            api_key = get_api_key_from_service(service_name)
            next_billing = datetime.now() + timedelta(days=365 if billing_cycle == "Annual" else 30)
        elif not api_key:
            api_key = getpass(f"Enter API Key for {service_name}: ")
            next_billing = None

        with open(self.storage_file, "r") as f:
            data = json.load(f)
        data[service_name] = {
            "key": api_key,
            "paid": paid,
            "amount_usd": amount_usd if paid else 0,
            "billing_cycle": billing_cycle if paid else None,
            "next_billing": next_billing.isoformat() if next_billing else None
        }
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Added API key for {service_name}")

    def get_key(self, service_name):
        with open(self.storage_file, "r") as f:
            data = json.load(f)
        return data.get(service_name, {}).get("key", None)

    def list_services(self):
        with open(self.storage_file, "r") as f:
            data = json.load(f)
        return list(data.keys())

    def auto_renew_paid_apis(self):
        with open(self.storage_file, "r") as f:
            data = json.load(f)

        for service_name, info in data.items():
            if info.get("paid") and info.get("next_billing"):
                next_billing_date = datetime.fromisoformat(info["next_billing"])
                if datetime.now() >= next_billing_date:
                    print(f"Renewing subscription for {service_name}...")
                    if tps_global_deduct(info["amount_usd"], service_name):
                        info["next_billing"] = (datetime.now() + timedelta(days=365 if info["billing_cycle"] == "Annual" else 30)).isoformat()
                        info["key"] = get_api_key_from_service(service_name)
                        print(f"Renewed {service_name} successfully.")
                    else:
                        print(f"Failed to renew {service_name}.")

        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=4)

# --- Demo usage ---

def demo_usage():
    manager = ProscAPIKeyManager()

    # Free API
    manager.add_key('example_service', 'EXAMPLE_API_KEY')

    # Paid APIs
    manager.add_key('openweathermap', paid=True, amount_usd=120, billing_cycle="Annual")
    manager.add_key('google_maps', paid=True, amount_usd=200, billing_cycle="Annual")

    print('Retrieved OpenWeatherMap key:', manager.get_key('openweathermap'))
    print('Services:', manager.list_services())

    # Auto-renew any expired paid APIs
    manager.auto_renew_paid_apis()

if __name__ == '__main__':
    demo_usage()
