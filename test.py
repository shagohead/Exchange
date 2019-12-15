import requests
import pytest
from models import User, Transactions, connect


@pytest.mark.parametrize(
    "json_input, expected",
    [
        ({}, """Invalid registration data received. KeyError: 'email'"""),
        ({"password": "7772777", "initial_balance": 110,
          "account_number": '111111', "currency": "GBP"},
         """Invalid registration data received. KeyError: 'email'"""),
        ({"email": "user_3", "initial_balance": 110,
          "account_number": '111111', "currency": "GBP"},
         """Invalid registration data received. KeyError: 'password'"""),
        ({"email": "user_3", "password": "7772777",
          "initial_balance": 110, "currency": "GBP"},
         """Invalid registration data received. KeyError: 'account_number'"""),
        ({"email": "user_3", "password": "7772777",
          "account_number": '111111', "currency": "GBP"},
         """Invalid registration data received. KeyError: 'initial_balance'"""),
        ({"email": "user_3", "password": "7772777", "initial_balance": 110,
          "account_number": '111111', },
         """Invalid registration data received. KeyError: 'currency'"""),
        ({"email": "xxx", "password": "7772777", "initial_balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "Email should contain at least 6 symbols"),
        ({"email": "xxxxxxx", "password": "7772777", "initial_balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "Email should contain @"),
        ({"email": "user_3@mail.ru", "password": "77", "initial_balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "Password should contain at least 3 symbols"),
        ({"email": "user_3@mail.ru", "password": "7772777",
          "initial_balance": 110, "account_number": '111111',
          "currency": "CAD"},
         "This currency is not acceptable"),
        ({"email": "user_3@mail.ru", "password": "7772777",
          "initial_balance": 110,
          "account_number": '1111117', "currency": "GBP"},
         "Account number should consist of 6 symbols"),
        ({"email": "user_3@mail.ru", "password": "7772777",
          "initial_balance": -110, "account_number": '111111',
          "currency": "GBP"}, "Balance can't be negative"),
        ({"email": "user_3@mail.ru", "password": "7772777",
          "initial_balance": 110, "account_number": '111111',
          "currency": "GBP"}, 'This login is busy. Please create another')
    ]
)
def test_user_registration_negative(json_input, expected):
    url = 'http://localhost:5000/registration'
    first_data = {"email": "user_3@mail.ru", "password": "7772777",
                  "initial_balance": 110, "account_number": '111111',
                  "currency": "GBP"}
    requests.post(url, json=first_data)
    response = requests.post(url, json=json_input)
    response = response.json()
    with connect() as session:  # очищаем таблицу
        session.query(User).delete()
    assert response['error'] == expected


def test_user_registration_positive():
    url = 'http://localhost:5000/registration'
    first_data = {"email": "user_3@mail.ru", "password": "7772777",
                  "initial_balance": 110, "account_number": '111111',
                  "currency": "GBP"}
    response = requests.post(url, json=first_data)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['details'] == 'new user has been registered successfully'


@pytest.mark.parametrize(
    "json_input, expected",
    [
        ('{}', "Unexpected error occurred: string indices must be integers"),
        ({"password": "7772777"}, """Invalid registration data received. KeyError: 'email'"""),
        ({"email": "user_3@mail.ru"},
         """Invalid registration data received. KeyError: 'password'"""),
        ({"email": "user_3333@mail.ru", "password": "7772777"},
         "Access denied. This login does not exist"),
        ({"email": "user_3@mail.ru", "password": "777"},
         "Access denied. Invalid password")
    ]
)
def test_login_negative(json_input, expected):
    url = 'http://localhost:5000/registration'
    first_data = {"email": "user_3@mail.ru", "password": "7772777",
                  "initial_balance": 110, "account_number": '111111',
                  "currency": "GBP"}  # регистрируем юзера
    requests.post(url, json=first_data)
    url = 'http://localhost:5000/login'
    response = requests.post(url, json=json_input)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['error'] == expected


def test_login_positive():
    url = 'http://localhost:5000/registration'
    test_user_data = {"email": "user_3@mail.ru", "password": "7772777",
                      "initial_balance": 110, "account_number": '111111',
                      "currency": "GBP"}
    requests.post(url, json=test_user_data)  # регистрируем юзера
    url = 'http://localhost:5000/login'
    data = {"email": "user_3@mail.ru", "password": "7772777"}
    response = requests.post(url, json=data)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['details'] == "successful authorization"


@pytest.mark.parametrize(
    "json_input, expected",
    [
        ('{}', "Unexpected error occurred: string indices must be integers"),
        ({"receivers_account": "444444", "amount": 30},
         """Invalid registration data received. KeyError: 'senders_account'"""),
        ({"senders_account": "123456", "amount": 30},
         """Invalid registration data received. KeyError: 'receivers_account'"""),
        ({"senders_account": "123456", "receivers_account": "444444"},
         """Invalid registration data received. KeyError: 'amount'"""),
        ({"senders_account": "12345677", "receivers_account": "444444",
          "amount": 30}, "Account of sender does not exist"),
        ({"senders_account": "123456", "receivers_account": "44444477",
          "amount": 30}, "Account of receiver does not exist"),
        ({"senders_account": "123456", "receivers_account": "444444",
          "amount": -30}, "You can't send negative amount"),
        ({"senders_account": "123456", "receivers_account": "444444",
          "amount": 10000}, "Not enough funds")
    ]
)
def test_transaction_negative(json_input, expected):
    url = 'http://localhost:5000/registration'
    senders_data = {"email": "user_3@mail.ru", "password": "7772777",
                    "initial_balance": 110, "account_number": '123456',
                    "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"email": "user_2@mail.ru", "password": "7772777",
                      "initial_balance": 110, "account_number": '444444',
                      "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    response = requests.post(url, json=json_input)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['error'] == expected


def test_transaction_positive():
    url = 'http://localhost:5000/registration'
    senders_data = {"email": "user_3@mail.ru", "password": "7772777",
                    "initial_balance": 110, "account_number": '123456',
                    "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"email": "user_2@mail.ru", "password": "7772777",
                      "initial_balance": 110, "account_number": '444444',
                      "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    transaction_data = {"senders_account": "123456",
                        "receivers_account": "444444", "amount": 10}
    response = requests.post(url, json=transaction_data)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['details'] == 'success'


def test_get_statement_negative():
    url = 'http://localhost:5000/registration'
    senders_data = {"email": "user_3@mail.ru", "password": "7772777",
                    "initial_balance": 110, "account_number": '123456',
                    "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"email": "user_2@mail.ru", "password": "7772777",
                      "initial_balance": 110, "account_number": '444444',
                      "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    transaction_data = {"senders_account": "123456",
                        "receivers_account": "444444", "amount": 10}
    requests.post(url, json=transaction_data)  # создаем исходящую транзакцию
    url = 'http://localhost:5000/statement/1234567'
    response = requests.get(url)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['error'] == "Account does not exist"


def test_get_statement_positive():
    url = 'http://localhost:5000/registration'
    senders_data = {"email": "user_3@mail.ru", "password": "7772777",
                    "initial_balance": 110, "account_number": '123456',
                    "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"email": "user_2@mail.ru", "password": "7772777",
                      "initial_balance": 110, "account_number": '444444',
                      "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    transaction_data = {"senders_account": "123456",
                        "receivers_account": "444444", "amount": 10}
    requests.post(url, json=transaction_data)  # первая исходящая транзакция
    transaction_data = {"senders_account": "444444",
                        "receivers_account": "123456", "amount": 15}
    requests.post(url, json=transaction_data)  # первая входящая транзакция
    transaction_data = {"senders_account": "123456",
                        "receivers_account": "444444", "amount": 20}
    requests.post(url, json=transaction_data)  # вторая исходящая транзакция
    transaction_data = {"senders_account": "444444",
                        "receivers_account": "123456", "amount": 25}
    requests.post(url, json=transaction_data)  # вторая входящая транзакция
    url = 'http://localhost:5000/statement/123456'
    response = requests.get(url)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
        session.query(Transactions).delete()
    assert bool(response['transactions']) is True