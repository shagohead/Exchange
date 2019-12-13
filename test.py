import requests
import json
import pytest
from models import User, Session, Transactions, Currency, connect


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ({}, "JSON does not contain required data"),
        ({ "password": "7772777", "balance" : 110,
          "account_number": '111111', "currency" : "GBP"  },
         "JSON does not contain required data"),
        ({"login": "user_3", "balance" : 110,
          "account_number": '111111', "currency" : "GBP"  },
         "JSON does not contain required data" ),
        ({"login": "user_3", "password": "7772777", "balance" : 110, "currency" : "GBP"  },
         "JSON does not contain required data"),
        ({"login": "user_3", "password": "7772777", "account_number": '111111', "currency" : "GBP"  },
         "JSON does not contain required data"),
        ({"login": "user_3", "password": "7772777", "balance" : 110,
          "account_number": '111111',},  "JSON does not contain required data"),
        ({"login": "xxx", "password": "7772777", "balance" : 110,
          "account_number": '111111', "currency" : "GBP"  },
         "Login should contain at least 7 symbols"),
        ({"login": "xxxxxxx", "password": "7772777", "balance" : 110,
         "account_number": '111111', "currency" : "GBP"  },
         "Login should contain @"),
        ({"login": "user_3@mail.ru", "password": "77", "balance" : 110,
        "account_number": '111111', "currency" : "GBP"  },
        "Password should contain at least 3 symbols"),
        ({"login": "user_3@mail.ru", "password": "7772777", "balance" : 110,
          "account_number": '1111117', "currency" : "GBP"  },
         "Account number should consist of 6 symbols"),
        ({"login": "user_3@mail.ru", "password": "7772777", "balance" : -110,
          "account_number": '111111', "currency" : "GBP"  }, "Balance can't be negative"),
        ({"login": "user_3@mail.ru", "password": "7772777", "balance" : 110,
          "account_number": '111111', "currency" : "GBP"  }, 'This login is busy. Please create another')
    ]
)


def test_user_registration_negative(JSON_input, expected):
     url = 'http://localhost:5000/registration'
     first_data = {"login": "user_3@mail.ru", "password": "7772777", "balance" : 110,
          "account_number": '111111', "currency" : "GBP" }
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
    with connect() as session:  # очищаем таблицу
        operation_result = session.query(User).delete()
    assert response['data'] == 'new user has been registered successfully'


@pytest.mark.parametrize(
    "JSON_input, expected",
    [
        ('{}', "JSON does not contain required data"),
        ({"password": "7772777"}, "JSON does not contain required data"),
        ({"login": "user_3@mail.ru"}, "JSON does not contain required data" ),
        ({"login": "user_3333@mail.ru", "password": "7772777"}, "Access denied. This login does not exist"),
        ({"login": "user_3@mail.ru", "password": "777"}, "Access denied. Invalid password")
    ]
)

def test_auth_negative(JSON_input, expected):
    url = 'http://localhost:5000/registration'
    first_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                  "account_number": '111111', "currency": "GBP"}  # регистрируем юзера
    requests.post(url, json=first_data)
    url = 'http://localhost:5000/auth'
    response = requests.post(url, json=JSON_input)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert response['error'] == expected


def test_auth_positive():
    url = 'http://localhost:5000/registration'
    first_data = {"login": "user_3@mail.ru", "password": "7772777", "balance": 110,
                  "account_number": '111111', "currency": "GBP"}  # регистрируем юзера

    url = 'http://localhost:5000/auth'
    data = {"login": "user_3@mail.ru", "password": "7772777"}
    response = requests.post(url, json=data)
    response = response.json()
    with connect() as session:
        operation_result = session.query(User).delete()
    assert bool(response['data']) is True


