from logging import exception


def add(num_1: int, num_2: int):
    return num_1 + num_2


def subtract(num_1: int, num_2: int):
    return num_1 - num_2


def multiply(num_1: int, num_2: int):
    return num_1 * num_2


def divide(num_1: int, num_2: int):
    return num_1 / num_2

class InsufficientFunds(Exception):
    pass

class BankAccount():
    def __init__(self, starting_balance =0):
        self.balance = starting_balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        # if amount > self.balance:
        #     raise Exception("Insufficient Funds")
        self.balance -= amount

    def collect_interst(self):
        self.balance *= 1.1