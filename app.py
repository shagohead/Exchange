from flask import Flask, jsonify, request
from models import User, Session, Transactions, Currency, connect
import datetime
from const import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_OK

app = Flask(__name__)


@app.route('/')
def index():
    return 'index'

def converter(currency_1, currency_2, sum_1):
    base = 'USD'
    with connect() as session:
        course_currency_1 = session.query(Currency.course).filter(
                Currency.short_name == currency_1).first()
        course_currency_1 = course_currency_1[0]
        multiplicity_currency_1 = session.query(Currency.multiplicity).filter(
                Currency.short_name == currency_1).first()
        multiplicity_currency_1 = multiplicity_currency_1[0]
        course_currency_2 = session.query(Currency.course).filter(
            Currency.short_name == currency_2).first()
        course_currency_2 = course_currency_2[0]
        multiplicity_currency_2 = session.query(Currency.multiplicity).filter(
            Currency.short_name == currency_2).first()
        multiplicity_currency_2 = multiplicity_currency_2[0]
    if currency_1 == base:
        sum_2 = (course_currency_2 * sum_1)/multiplicity_currency_2
        return sum_2
    if currency_2 == base:
        sum_2 = (multiplicity_currency_2 * sum_1)/course_currency_2
        return sum_2
    sum_2 = (multiplicity_currency_1 * sum_1 * course_currency_2) / (multiplicity_currency_2 * course_currency_1)
    return sum_2


@app.route('/registration', methods=['POST'])
def user_registration():
    result = {}
    status_code = HTTP_OK
    json = request.get_json() # получаем json из POST запроса
    try:
        balance = json['balance']
        currency = json['currency']
        login = json['login']
        account_number = json['account_number']
        password = json['password']
        if len(login) < 1:
            result['error'] = "Login should contain at least one symbol"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
        if len(password) < 3:
            result['error'] = "Password should contain at least 3 symbols"
            print(result)  # выводим лог в stdout
            status_code = HTTP_BAD_REQUEST
            return jsonify(result), status_code
    except Exception as e:
        print(repr(e))  # выводим лог в stdout
        result['error'] = "JSON does not contain required data"
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    with connect() as session:
        existed_user = session.query(User.login).filter(
                User.login == login).first()  # проверяем есть ли уже в базе пользователь с заданным логином
    if existed_user is not None:
        raise Exception('This login is busy. Please create another')
    new_user_info = User(login, password, account_number, balance, currency)
    with connect() as session:
        session.add(new_user_info)
    result['data'] = 'new user has been registered successfully'
    return jsonify(result), status_code


@app.route('/auth', methods=['POST'])
def user_auth():
    result = {}
    status_code = HTTP_OK
    json = request.get_json(force=True)
    try:
        current_login = json['login']
        current_password = json['password']
    except Exception as e:
        result['error'] = "JSON does not contain required data"
        print(repr(e))  # выводим лог в stdout
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    with connect() as session:
        password = session.query(User.password).filter(User.login == current_login).first() # проверяем есть ли пользователь с заданным логином. если да получаем хеш пароля данного пользователя
    if password == None:
        raise Exception('Access denied. This login does not exist')
    password = password[0]
    if current_password != password:
        raise Exception('Access denied. Invalid password')
    result['data'] = 'successful authorization'
    return jsonify(result), status_code


@app.route('/transaction', methods=['POST'])
def transaction():
    result = {}
    status_code = HTTP_OK
    json = request.get_json()  # получаем json из POST запроса
    try:
        senders_account = json['senders_account']
        receivers_account = json['receivers_account']
        amount = json['amount']
        amount_to_receive = amount
    except Exception as e:
        print(repr(e))  # выводим лог в stdout
        result['error'] = "JSON does not contain required data"
        status_code = HTTP_BAD_REQUEST
        return jsonify(result), status_code
    with connect() as session:
        senders_account_status = session.query(User.login).filter(
            User.account_number == senders_account).first()  # проверяем есть ли отправитель
        receivers_account_status = session.query(User.login).filter(
            User.account_number == receivers_account).first()  # проверяем есть ли получатель
        senders_balance = session.query(User.balance).filter(
            User.account_number == senders_account).first() # проверяем баланс отправителя
        receivers_balance = session.query(User.balance).filter(
            User.account_number == receivers_account).first() # берем баланс получателя
        senders_currency = session.query(User.currency).filter(
            User.account_number == senders_account).first() # берем валюту отправителя
        receivers_currency = session.query(User.currency).filter(
            User.account_number == receivers_account).first() # берем валюту получателя
    if senders_account_status == None:
        result['error'] = "Account of sender does not exists"
    if receivers_account_status == None:
        result['error'] = "Account of receiver does not exists"
    senders_balance = senders_balance[0]
    senders_balance -= amount
    if senders_balance < 0:
        result['error'] = "Not enough funds"
    if senders_currency != receivers_currency:
        amount_to_receive = converter(senders_currency, receivers_currency, amount)
    receivers_balance = receivers_balance[0]
    receivers_balance += amount_to_receive
    date_time = datetime.datetime.today()
    date_time = date_time.strftime("%Y-%m-%d-%H.%M.%S")
    new_transaction = Transactions(date_time, senders_account, receivers_account, amount, senders_currency)
    with connect() as session:
        session.add(new_transaction) # добавляем новую запись в таблицу транзакций
        session.query(User).filter(User.account_number == senders_account).update({User.balance: senders_balance}) # обновляем баланс отправителя
        session.query(User).filter(User.account_number == receivers_account).update({User.balance: receivers_balance}) # обновляем баланс получателя
    result['data'] = 'success'
    return jsonify(result), status_code


@app.route('/statement/<account_number>', methods=['GET'])
def get_statement(account_number):
    result = {}
    status_code = HTTP_OK
    with connect() as session:
        income_transactions = session.query(Transactions).filter(
            Transactions.receivers_account == account_number)
        outcome_transactions = session.query(Transactions).filter(
            Transactions.senders_account == account_number)
    income = {}
    outcome = {}
    for item in income_transactions:
        print(item.amount)
        cur_dict = {}
        cur_dict['senders_account'] = item.senders_account
        cur_dict['receivers_account'] = item.receivers_account
        cur_dict['amount'] = item.amount
        cur_dict['currency'] = item.currency
        cur_dict['type'] = 'income'
        date_time = item.date_time
        income[date_time] = cur_dict
    for item in outcome_transactions:
        cur_dict ={}
        cur_dict['senders_account'] = item.senders_account
        cur_dict['receivers_account'] = item.receivers_account
        cur_dict['amount'] = item.amount
        cur_dict['currency'] = item.currency
        cur_dict['type'] = 'outcome'
        date_time = item.date_time
        outcome[date_time] = cur_dict
    income.update(outcome)
    result['transactions'] = income
    return jsonify(result), status_code


if __name__ == '__main__':
    app.run()
