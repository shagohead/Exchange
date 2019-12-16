from models import connect, Currency
from flask import jsonify
import status_codes as status


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
    sum_2 = (multiplicity_currency_1 *
             sum_1 * course_currency_2) / (multiplicity_currency_2 *
                                           course_currency_1)
    return sum_2


def gather_transactions(list_of_transactions, type_of_transaction):
    final_dict = {}
    for item in list_of_transactions:
        cur_dict = {}
        cur_dict['senders_account'] = item.senders_account
        cur_dict['receivers_account'] = item.receivers_account
        cur_dict['amount'] = item.amount
        cur_dict['currency'] = item.currency
        cur_dict['type'] = type_of_transaction
        date_time = item.date_time
        final_dict[date_time] = cur_dict
    return final_dict


def get_final_statement(income, outcome):
    income.update(outcome)
    sorted_keys = sorted(income)
    final_statement = {}
    for item in sorted_keys:
        final_statement[item] = income[item]
    return final_statement


def encrypt_password(password):
    """
    Pretend we encrypt password.
    """
    return password


def process_errors(data: tuple):
    list_of_currencies = ['USD', 'GBP', 'RUB', 'BTC', 'EUR']
    email, password, account_number, balance, entered_currency = data
    result = {}
    if len(email) < 6:
        result['error'] = "Email should contain at least 6 symbols"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if '@' not in email:
        result['error'] = "Email should contain @"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if len(password) < 3:
        result['error'] = "Password should contain at least 3 symbols"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if len(str(account_number)) != 6:
        result['error'] = "Account number should consist of 6 symbols"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if balance < 0:
        result['error'] = "Balance can't be negative"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if balance < 0:
        result['error'] = "Balance can't be negative"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
    if entered_currency not in list_of_currencies:
        result['error'] = "This currency is not acceptable"
        status_code = status.HTTP_BAD_REQUEST
        return jsonify(result), status_code
