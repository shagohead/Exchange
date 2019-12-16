"""
REST API app.
"""
from flask import Flask, jsonify, request
from models import User, Transactions, connect
import datetime
import status_codes as status
import utils

app = Flask(__name__)


@app.route('/registration', methods=['POST'])
def user_registration():
    result = {}
    status_code = status.HTTP_OK
    request_data = request.get_json()  # получаем json из POST запроса
    try:
        email = request_data['email']
        password = request_data['password']
        account_number = request_data['account_number']
        balance = request_data['initial_balance']
        currency = request_data['currency']
        error = utils.process_errors((email, password, account_number, balance, currency))
        if error:
            return error
    except KeyError as ex:
        result['error'] = f"Invalid registration data received. KeyError: {ex}"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    except Exception as e:
        result['error'] = f"Unexpected error occurred: {e}"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    with connect() as session:
        existed_user = session.query(User.email).filter(
                User.email == email).first()
    if existed_user:
        result['error'] = 'This login is busy. Please create another'
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    password = utils.encrypt_password(password)
    new_user_info = User(email, password, account_number, balance, currency)
    with connect() as session:
        session.add(new_user_info)
    result['details'] = 'new user has been registered successfully'
    return jsonify(result), status_code


@app.route('/login', methods=['POST'])
def user_login():
    result = {}
    status_code = status.HTTP_OK
    request_data = request.get_json()  # получаем json из POST запроса
    try:
        current_email = request_data['email']
        current_password = request_data['password']
    except KeyError as ex:
        result['error'] = f"Invalid registration data received. KeyError: {ex}"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    except Exception as e:
        result['error'] = f"Unexpected error occurred: {e}"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    with connect() as session:
        password = session.query(User.password).filter(User.email
                                                       == current_email).first()
    if not password:
        result['error'] = "Access denied. This login does not exist"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    password = password[0]
    if current_password != password:
        result['error'] = "Access denied. Invalid password"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    result['details'] = 'successful authorization'
    return jsonify(result), status_code


@app.route('/transaction', methods=['POST'])
def transaction():
    result = {}
    status_code = status.HTTP_OK
    request_data = request.get_json()  # получаем json из POST запроса
    try:
        senders_account = request_data['senders_account']
        receivers_account = request_data['receivers_account']
        amount = request_data['amount']
        amount_to_receive = amount
    except KeyError as ex:
        result['error'] = f"Invalid registration data received. KeyError: {ex}"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    except Exception as e:
        result['error'] = f"Unexpected error occurred: {e}"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if amount < 0:
        result['error'] = "You can't send negative amount"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    with connect() as session:
        sender = session.query(User.email).filter(
            User.account_number == senders_account).first()
        receiver = session.query(User.email).filter(
            User.account_number == receivers_account).first()
        senders_balance = session.query(User.balance).filter(
            User.account_number == senders_account).first()
        receivers_balance = session.query(User.balance).filter(
            User.account_number == receivers_account).first()
        senders_currency = session.query(User.currency).filter(
            User.account_number == senders_account).first()
        receivers_currency = session.query(User.currency).filter(
            User.account_number == receivers_account).first()
    if not sender:
        result['error'] = "Account of sender does not exist"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if not receiver:
        result['error'] = "Account of receiver does not exist"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    senders_balance = senders_balance[0]
    if (senders_balance - amount) < 0:
        result['error'] = "Not enough funds"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    senders_balance -= amount
    if senders_currency != receivers_currency:
        amount_to_receive = utils.converter(senders_currency,
                                            receivers_currency, amount)
    receivers_balance = receivers_balance[0]
    receivers_balance += amount_to_receive
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%Y-%m-%d-%H.%M.%S")
    new_transaction = Transactions(timestamp, senders_account,
                                   receivers_account, amount, senders_currency)
    with connect() as session:
        session.add(new_transaction)
        session.query(User).filter(User.account_number
                                   == senders_account).update({User.balance:
                                                                           senders_balance})
        session.query(User).filter(User.account_number
                                   == receivers_account).update({User.balance:
                                                                             receivers_balance})
    result['details'] = 'success'
    return jsonify(result), status_code


@app.route('/statement/<account_number>', methods=['GET'])
def get_statement(account_number):
    result = {}
    status_code = status.HTTP_OK
    with connect() as session:
        account_status = session.query(User.email).filter(
            User.account_number == account_number).first()
        if not account_status:
            result['error'] = "Account does not exist"
            status_code = status.HTTP_BAD_REQUEST
            return jsonify(result), status_code
        income_transactions = session.query(Transactions).filter(
            Transactions.receivers_account == account_number)
        outcome_transactions = session.query(Transactions).filter(
            Transactions.senders_account == account_number)
    income = utils.gather_transactions(income_transactions, 'income')
    outcome = utils.gather_transactions(outcome_transactions, 'outcome')
    result['transactions'] = utils.get_final_statement(income, outcome)
    return jsonify(result), status_code


if __name__ == '__main__':
    app.run()
