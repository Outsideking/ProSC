"""
bankSC.py - Bank Simulation Client
สามารถต่อยอดเชื่อม PSP/ธนาคารจริง
"""

class Common:
    @staticmethod
    def log(msg):
        print(f"[BANKSC] {msg}")

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
