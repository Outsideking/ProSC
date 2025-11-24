"""
run.py - BankSC Full Simulation Client + Web Dashboard
สามารถสร้างบัญชี, ตรวจสอบ, โอนจ่าย, รับเงิน simulation
พร้อมเว็บ dashboard
"""

import threading
import time
from flask import Flask, jsonify, render_template_string

# -------------------------
# Common Helper
# -------------------------
class Common:
    @staticmethod
    def log(msg):
        print(f"[BANKSC] {msg}")

# -------------------------
# Bank Simulation
# -------------------------
class BankAccount:
    def __init__(self, country, name, balance=0):
        self.country = country
        self.name = name
        self.balance = balance
        Common.log(f"Account created: {self.name} ({self.country}) balance={self.balance}")

    def deposit(self, amount):
        self.balance += amount
        Common.log(f"Deposit {amount} -> {self.name} new balance={self.balance}")

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            Common.log(f"Withdraw {amount} -> {self.name} new balance={self.balance}")
            return True
        Common.log(f"Withdraw failed: insufficient funds in {self.name}")
        return False

class BankSystem:
    def __init__(self):
        self.accounts = {}

    def create_account(self, country, name, balance=0):
        acc = BankAccount(country, name, balance)
        self.accounts[name] = acc
        return acc

    def transfer(self, from_acc, to_acc, amount):
        if from_acc.withdraw(amount):
            to_acc.deposit(amount)
            Common.log(f"Transfer {amount} from {from_acc.name} to {to_acc.name} complete.")
            return True
        return False

# -------------------------
# Bank Client Simulation
# -------------------------
bank = BankSystem()
# ตัวอย่างบัญชีเริ่มต้น
acc1 = bank.create_account("Thailand", "TH_Account1", 1000)
acc2 = bank.create_account("USA", "US_Account1", 500)

# -------------------------
# Web Dashboard
# -------------------------
app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BankSC Dashboard</title>
</head>
<body>
<h1>BankSC Accounts Dashboard</h1>
<ul>
    {% for name, balance in accounts.items() %}
        <li>{{name}} ({{countries[name]}}): {{balance}}</li>
    {% endfor %}
</ul>

<h2>Transfer Money</h2>
<form action="/transfer" method="get">
    From: <input type="text" name="from_acc"><br>
    To: <input type="text" name="to_acc"><br>
    Amount: <input type="number" name="amount"><br>
    <input type="submit" value="Transfer">
</form>
</body>
</html>
"""

@app.route("/")
def index():
    accounts = {name: acc.balance for name, acc in bank.accounts.items()}
    countries = {name: acc.country for name, acc in bank.accounts.items()}
    return render_template_string(INDEX_HTML, accounts=accounts, countries=countries)

@app.route("/transfer")
def transfer():
    from flask import request
    from_acc = request.args.get("from_acc")
    to_acc = request.args.get("to_acc")
    amount = int(request.args.get("amount", 0))
    if from_acc in bank.accounts and to_acc in bank.accounts:
        success = bank.transfer(bank.accounts[from_acc], bank.accounts[to_acc], amount)
        return jsonify({"success": success})
    return jsonify({"success": False, "error": "Account not found"})

def run_web():
    app.run(host="0.0.0.0", port=5000)

# -------------------------
# Auto Transaction Simulation
# -------------------------
def auto_transactions():
    while True:
        bank.transfer(acc1, acc2, 10)
        bank.transfer(acc2, acc1, 5)
        time.sleep(10)

# -------------------------
# Main
# -------------------------
def main():
    Common.log("BankSC simulation starting...")

    # Run web dashboard
    threading.Thread(target=run_web, daemon=True).start()
    Common.log("Web dashboard running at http://localhost:5000")

    # Run auto transaction simulation
    threading.Thread(target=auto_transactions, daemon=True).start()

    # Keep main thread alive
    while True:
        time.sleep(5)

if __name__ == "__main__":
    main()
