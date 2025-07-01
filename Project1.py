import csv
import random
from datetime import datetime
from abc import ABC, abstractmethod
import os
import logging

# ------- CONFIGURATION  ------- #
csv_file = "oop_banking.csv"
log_file = "bank_log.txt"

# ------- LOGGING SET UP  ------- #
logging.basicConfig(
    filename = log_file,
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

class Transaction:
    """Gives information about an account's transaction history"""
    def __init__(self, amount, transaction_type, current_balance, date=None):
        """
        Initializes a transaction.

        Args:
            amount (float): Amount involved in the transaction
            transaction_type (str): Etiher "Deposit" or "Withdrawal"
            current_balance (float): Current balance after transaction occured.
            date (datetime): Timestamp of the transaction. Defaults to now.
        """
        self.amount = amount
        self.type = transaction_type
        self.date = date if date else datetime.now()
        self.current_balance = current_balance

    def __str__(self):
        return (f"{self.date} - {self.type} - ${self.amount}"
               f"\nBalance: ${self.current_balance}")
    
class BankAccount(ABC):
    """Base class for all bank accounts."""

    def __init__(self, account_number, first_name, last_name,gender, account_type, balance = 0.0, transaction = None):
        """Initializes a bank account
        Args:
            account_number (str): Unique account number.
            first_name (str): Account holder's first name.
            last_name (str): Account holder's last name.
            gender (str): Gender of the account holder.
            account_type (str): Either "savings" or "checking".
            balance (float, optional): Starting balance. Defaults to 0.0.
            transactions (list, optional): List of past Transaction objects.
        """
        self.account_number = account_number
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.account_type = account_type
        self.balance = float(balance)
        self.transaction = transaction if transaction else []

    def deposit(self, amount):
        """"A method or function which deposits a specified amount into account and records the transaction"""
        if amount >= 0:
            self.balance += amount
            self.transaction.append(Transaction(amount, "Deposit", self.balance))
        else: 
            raise ValueError("Amount must be non-negative!")

    def withdraw(self, amount):
        if amount >= 0:
            if 0 <= amount <= self.balance:
                self.balance -= amount
                self.transaction.append(Transaction(amount, "Withdrawal", self.balance))
            else: 
                raise ValueError("Insufficient funds.")
        else:
            raise ValueError("Amount must be non-negative!")
        
    def get_transaction_history(self):
        return "\n".join(str(t) for t in self.transaction)
    
    def to_dict(self):
        return{
            "account_number": self.account_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "account_type": self.account_type,
            "balance": self.balance,
            "transactions": "|".join(str(t) for t in self.transaction)
        }
    @abstractmethod
    def account_summary(self):
        """Allows sub classes (SavingsAccount and CheckingAccount) to write themselves to specify account type"""
        pass

    @classmethod
    def from_dict(cls, data):
        """Rebuilds a BankAccount(or subclass) from a dictionary loaded from a CSV file row."""
        transaction = []
        if data.get("transaction"):
            for entry in data["transaction"].split("|"):
                parts = entry.split("-")
            if len(parts) == 4:
                try:
                    date = datetime.fromisoformat(parts[0])
                    t_type = parts[1]
                    amount = float(parts[2].replace("$", ""))
                    balance = float(parts[3].split(": ")[-1])
                    transaction.append(Transaction(amount, t_type, balance, date))
                except Exception:
                    pass
        
        account_type = data["account_type"].lower()
        args = (
            data["account_number"],
            data["first_name"],
            data["last_name"],
            data["gender"],
            float(data["balance"]),
            transaction
        )

        if account_type == "savings":
            return SavingsAccount(*args)
        elif account_type == "checking":
            checkbook_issued = data.get("checkbook_issued", "False").lower == "true"
            return CheckingAccount(*args, checkbook_issued=checkbook_issued)
        else:
            raise ValueError(f"Unknown account type: {account_type}")

# ------- SUBCLASSES  ------- # 
class SavingsAccount(BankAccount):
    """Savings account with a minimum balance requirement."""

    def __init__ (self, account_number, first_name, last_name, gender, balance=0.0, transactions = None, minimum_balance = 100):
        super().__init__(account_number, first_name, last_name, gender, "savings", balance, transactions)
        self.minimum_balance = minimum_balance
    
    def withdraw(self, amount):
        if self.balance - amount < self.minimum_balance:
            raise ValueError(f"Insufficient funds: Cannot go below minimum balance of ${self.minimum_balance} in a savings account.")
        super().withdraw(amount)

    def account_summary(self):
        return f"Savings Account {self.account_number}\n Balance: ${self.balance:.2f}"

class CheckingAccount(BankAccount):
    """Checking account with checkbook tracking"""

    def __init__(self, account_number, first_name, last_name, gender, balance=0.0, transactions=None, checkbook_issued=False):
        super().__init__(account_number, first_name, last_name, gender, "checking", balance, transactions)
        self.checkbook_issued = checkbook_issued

    def issue_checkbook(self):
        """Issues and marks whether a checkbook has been issued"""
        if not self.checkbook_issued:
            self.checkbook_issued = True
            print("Checkbook has been issued")
        else:
            print("Checkbook already issued.")

    def account_summary(self):
        return f"Checking Account {self.account_number}\n Balance: ${self.balance:.2f}"
    
    def to_dict(self):
        data = super().to_dict()
        data["checkbook_issued"] = self.checkbook_issued
        return data

# ------- CSV Utility Functions  ------- # 
def load_accounts():
    accounts = {}
    try:
        with open(csv_file, newline = '') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse transactions using from_dict
                acc = BankAccount.from_dict(row)

                # Checks whether account is checking then set the checkbook flag
                if isinstance(acc, CheckingAccount):
                    acc.checkbook_issued = row.get("checkbook_issued", "False").lower() == "true"

                accounts[acc.account_number] = acc

    except FileNotFoundError:
        pass #if there are no files created, it will create an empty file.
    return accounts

def save_accounts(accounts):
    with open(csv_file, mode = 'w', newline = '') as file:
        fieldnames = ["account_number", "first_name", "last_name", "gender",
                      "account_type", "balance", "transactions", "checkbook_issued"]
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writeheader()
        for acc in accounts.values():
            row = acc.to_dict()
            if isinstance(acc, CheckingAccount):
                row["checkbook_issued"] = acc.checkbook_issued
            else:
                row["checkbook_issued"] = "" # Savings account will have missings
            writer.writerow(acc.to_dict())
        
def generate_account_number(accounts):
    """Automatically generates the account numbers"""
    if not accounts:
        return "00001"
    
    existing_numbers = sorted(int(acc_num) for acc_num in accounts.keys())
    next_number = existing_numbers[-1]+1
    return f"{next_number:05d}" # pads with zeroes to make it 5 digits

# ------- Command Line Interface  ------- # 
def banking_cli():
    accounts = load_accounts()
    print("Welcome to Sheena's Banking")
    print("Commands: create, deposit, withdraw, show, exit")

    while True:
        cmd = input("\n> ").strip().lower()

        if cmd == "create":
            acc_num = generate_account_number(accounts)
            print(f"Assigned account number: {acc_num}")
            first = input("First Name: ")
            last = input("Last Name: ")
            gender = input("Gender (M/F/Other): ")
            acc_type = input("Type (savings/checking): ").lower()

            if acc_type == "savings":
                acc = SavingsAccount(acc_num, first, last, gender)
            elif acc_type == "checking":
                acc = CheckingAccount(acc_num, first, last, gender)
            else:
                print("Invalid account type.")
                continue

            accounts[acc_num] = acc
            save_accounts(accounts)
            logging.info(f"Created {acc_type} account {acc_num} for {first} {last}")
            print("Account created.")

        elif cmd in ("deposit", "withdraw"):
            acc_num = input("Account number: ")
            if acc_num not in accounts:
                print("Account not found.")
                continue

            try:
                amount = float(input("Amount: "))
                if cmd == "deposit":
                    accounts[acc_num].deposit(amount)
                    logging.info(f"Deposited ${amount} to account {acc_num}")
                    print("Deposit successful.")
                else:
                    accounts[acc_num].withdraw(amount)
                    logging.info(f"Withdrew ${amount} from account {acc_num}")
                    print("Withdrawal successful.")
                save_accounts(accounts)
            except Exception as e:
                logging.warning(f"Failed {cmd} on {acc_num}: {e}")
                print("Error:", e)

        elif cmd == "show":
            acc_num = input("Account number: ")
            if acc_num in accounts:
                acc = accounts[acc_num]
                logging.info(f"Viewed account {acc_num}")
                print(acc.account_summary())
                print(acc.get_transaction_history())

                # Allows user to issue a checkbook if checkbook has not yet been issued.
                if isinstance(acc, CheckingAccount) and not acc.checkbook_issued:
                    response = input("Checkbook on this Checking Account has not been issued. Issue checkbook? [y/n]: ").strip().lower()
                    if response == "y":
                        acc.issue_checkbook()
                        save_accounts(accounts)
                        logging.info(f"Issued checkbook to account {acc_num}")
                    else:
                        print("Account checkbook remains unissued.")
            else:
                print("Account not found.")

        elif cmd == "exit":
            logging.info("User exited the banking system.")
            print("Goodbye.")
            break

        else:
            print("Unknown command.")

# Execute in command prompt
if __name__ == "__main__":
    banking_cli()


# sample = BankAccount("12345", "Sheena", "Ondoy", "F", "checking")
# sample.deposit(100)
# sample.deposit(50)
# sample.deposit(-50)
# sample.withdraw(50)
# sample.withdraw(200)
# sample.withdraw(-100)
# print(sample.get_transaction_history())

# sample2 = SavingsAccount("12345", "Sheena", "Ondoy", "F")
# sample2.deposit(100)
# sample2.deposit(50)
# sample2.deposit(-50)
# sample2.withdraw(50)
# sample2.withdraw(200)
# sample2.withdraw(-100)
# print(sample2.get_transaction_history())
# sample2.withdraw(50)
# sample2.deposit(100)
# print(sample2.get_transaction_history())
# sample2.withdraw(50)
# sample2.withdraw(51)
# sample2.withdraw(50)
# print(sample2.get_transaction_history())
# print(sample2.account_summary())

# sample3 = CheckingAccount("12345", "Sheena", "Ondoy", "F")
# sample3.deposit(100)
# sample3.deposit(50)
# sample3.deposit(-50)
# sample3.withdraw(50)
# sample3.withdraw(200)
# sample3.withdraw(-100)
# print(sample3.get_transaction_history())
# sample3.withdraw(50)
# sample3.deposit(100)
# print(sample3.get_transaction_history())
# sample3.withdraw(50)
# sample3.withdraw(51)
# sample3.withdraw(50)
# print(sample3.get_transaction_history())
# print(sample3.account_summary())
# sample3.withdraw(50)