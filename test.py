import requests
import pytest
from models import User, Transactions, connect
import json


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ({}, "JSON does not contain required data"),
        ({"password": "7772777", "balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "JSON does not contain required data"),
        ({"login": "user_3", "balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "JSON does not contain required data"),
        ({"login": "user_3", "password": "7772777", "balance": 110, "currency": "GBP"},
         "JSON does not contain required data"),
        ({"login": "user_3", "password": "7772777", "account_number": '111111', "currency": "GBP"},
         "JSON does not contain required data"),
        ({"login": "user_3", "password": "7772777", "balance": 110,
          "account_number": '111111', }, "JSON does not contain required data"),
        ({"login": "xxx", "password": "7772777", "balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "Login should contain at least 7 symbols"),
        ({"login": "xxxxxxx", "password": "7772777", "balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "Login should contain @"),
        ({"login": "user_3@mail.ru", "password": "77", "balance": 110,
          "account_number": '111111', "currency": "GBP"},
         "Password should contain at least 3 symbols"),
        ({"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
          "account_number": '1111117', "currency": "GBP"},
         "Account number should consist of 6 symbols"),
        ({"login": "user_3@mail.ru", "password": "7772777", "balance": -110,
          "account_number": '111111', "currency": "GBP"}, "Balance can't be negative"),
        ({"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
          "account_number": '111111', "currency": "GBP"}, 'This login is busy. Please create another')
    ]
)
def test_user_registration_negative(JSON_input, expected):
    url = 'http://localhost:5000/registration'
    first_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                  "account_number": '111111', "currency": "GBP"}
    requests.post(url, json=first_data)
    response = requests.post(url, json=JSON_input)
    response = response.json()
    with connect() as session:  # очищаем таблицу
        session.query(User).delete()
    assert response['error'] == expected


def test_user_registration_positive():
    url = 'http://localhost:5000/registration'
    first_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                  "account_number": '111111', "currency": "GBP"}
    response = requests.post(url, json=first_data)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
    assert response['details'] == 'new user has been registered successfully'


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ('{}', "JSON does not contain required data"),
        ({"password": "7772777"}, "JSON does not contain required data"),
        ({"login": "user_3@mail.ru"}, "JSON does not contain required data"),
        ({"login": "user_3333@mail.ru", "password": "7772777"}, "Access denied. This login does not exist"),
        ({"login": "user_3@mail.ru", "password": "777"}, "Access denied. Invalid password")
    ]
)
def test_login_negative(JSON_input, expected):
    url = 'http://localhost:5000/registration'
    first_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                  "account_number": '111111', "currency": "GBP"}  # регистрируем юзера
    requests.post(url, json=first_data)
    url = 'http://localhost:5000/login'
    response = requests.post(url, json=JSON_input)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['error'] == expected


def test_login_positive():
    url = 'http://localhost:5000/registration'
    test_user_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                      "account_number": '111111', "currency": "GBP"}
    requests.post(url, json=test_user_data)  # регистрируем юзера
    url = 'http://localhost:5000/login'
    data = {"login": "user_3@mail.ru", "password": "7772777"}
    response = requests.post(url, json=data)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['details'] == "successful authorization"


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ('{}', "JSON does not contain required data"),
        ({"receivers_account": "444444", "amount": 30}, "JSON does not contain required data"),
        ({"senders_account": "123456", "amount": 30}, "JSON does not contain required data"),
        ({"senders_account": "123456", "receivers_account": "444444"},
         "JSON does not contain required data"),
        ({"senders_account": "12345677", "receivers_account": "444444", "amount": 30},
         "Account of sender does not exist"),
        ({"senders_account": "123456", "receivers_account": "44444477", "amount": 30},
         "Account of receiver does not exist"),
        ({"senders_account": "123456", "receivers_account": "444444", "amount": -30},
         "You can't send negative amount"),
        ({"senders_account": "123456", "receivers_account": "444444", "amount": 10000},
         "Not enough funds")

    ]
)
def test_transaction_negative(JSON_input, expected):
    url = 'http://localhost:5000/registration'
    senders_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                    "account_number": '123456', "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"login": "user_2@mail.ru", "password": "7772777", "balance": 110,
                      "account_number": '444444', "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    response = requests.post(url, json=JSON_input)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['error'] == expected


def test_transaction_positive():
    url = 'http://localhost:5000/registration'
    senders_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                    "account_number": '123456', "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"login": "user_2@mail.ru", "password": "7772777", "balance": 110,
                      "account_number": '444444', "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    transaction_data = {"senders_account": "123456", "receivers_account": "444444", "amount": 10}
    response = requests.post(url, json=transaction_data)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['details'] == 'success'


def test_get_statement_negative():
    url = 'http://localhost:5000/registration'
    senders_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                    "account_number": '123456', "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"login": "user_2@mail.ru", "password": "7772777", "balance": 110,
                      "account_number": '444444', "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    transaction_data = {"senders_account": "123456", "receivers_account": "444444", "amount": 10}
    requests.post(url, json=transaction_data)  # создаем первую исходящую транзакцию
    url = 'http://localhost:5000/statement/1234567'
    response = requests.get(url)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['error'] == "Account does not exist"


def test_get_statement_positive():
    url = 'http://localhost:5000/registration'
    senders_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                    "account_number": '123456', "currency": "GBP"}
    requests.post(url, json=senders_data)  # регистрируем отправителя
    recievers_data = {"login": "user_2@mail.ru", "password": "7772777", "balance": 110,
                      "account_number": '444444', "currency": "GBP"}
    requests.post(url, json=recievers_data)  # регистрируем получателя
    url = 'http://localhost:5000/transaction'
    transaction_data = {"senders_account": "123456", "receivers_account": "444444", "amount": 10}
    requests.post(url, json=transaction_data)  # создаем первую исходящую транзакцию
    transaction_data = {"senders_account": "444444", "receivers_account": "123456", "amount": 15}
    requests.post(url, json=transaction_data)  # создаем первую входящую транзакцию
    transaction_data = {"senders_account": "123456", "receivers_account": "444444", "amount": 20}
    requests.post(url, json=transaction_data)  # создаем вторую исходящую транзакцию
    transaction_data = {"senders_account": "444444", "receivers_account": "123456", "amount": 25}
    requests.post(url, json=transaction_data)  # создаем вторую входящую транзакцию
    url = 'http://localhost:5000/statement/123456'
    response = requests.get(url)
    response = response.json()
    with connect() as session:
        session.query(User).delete()
        session.query(Transactions).delete()
    assert bool(response['transactions']) is True