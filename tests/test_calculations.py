import pytest
from app.calculations import add, subtract, multiply, divide, BankAccount

@pytest.fixture
def zero_bank_account():
    print("Creating empty bank account")
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(100)

@pytest.mark.parametrize("num1, num2, expected", [ 
    (1000, 500, 1500),
    (200, 40, 240),
    (55, 55, 110)
])


def test_sum(num1, num2, expected):
    print("printing Sum below")
    assert add(num1, num2) == expected
     
def test_subtract():
    assert subtract(9000, 1) == 8999

def test_multiply():
    assert multiply(4, 7) == 28

def test_divide():
    assert divide(20, 5) == 4

def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 100

def test_bank_default_amount(zero_bank_account):
    print("Opening it")
    assert zero_bank_account.balance == 0

def test_bank_deposit_amount(bank_account):
    bank_account.deposit(200)
    assert bank_account.balance == 300

def test_withdraw(bank_account):
    bank_account.withdraw(200)
    assert bank_account.balance == -100

def test_collect_interest(bank_account):
    bank_account.collect_interst()
    assert round(bank_account.balance, 2) == 110


@pytest.mark.parametrize("deposited, withdrew, expected", [ 
    (1000, 500, 500),
    (200, 40, 160),
    (55, 55, 0)
])


def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected
