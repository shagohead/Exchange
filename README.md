### Техническое Задание
Реализовать REST API, которое позволяет  выполнять следующие действия:
- зарегистрировать пользователя с указанием
- - начальный баланс
- - валюта счета
- - email (уникальный; используется для входа)
- - пароль
- аутентифицировать пользователя по почте и паролю
- перевести средства со своего счета на счет другого пользователя (используйте формулу конвертации, если валюты счетов отличаются)
- просмотреть список всех операций по своему счету

Система должна поддерживать следующие валюты: EUR, USD, GPB, RUB, BTC

##### Требования к системе
система должна быть реализована на любом python-фреймворке на ваш выбор: Django, Flask, aiohttp, Sanic, Bottle и пр
для хранения данных должна использоваться СУБД Postgres
код должен быть покрыт unit-тестами

### Бэкенд.
Бэкенд реализован на Flask

### Базы данных
В качестве ORM используется sqlalchemy. 

### Основные файлы приложения
- app.py - главный модуль приложения
- utils.py - модуль со вспомогательными функциями
- test.py - модуль с тестами для приложения

## Краткая инструкция

#### 1.Регистрация пользователя
при регистрации указываются:
- начальный баланс
- валюта счета
- email (уникальный; используется для входа)
- пароль

данные передаются посредством POST запроса.
###### пример запроса:
```bash
curl -d '{"email": "user_3@mail.ru", "password": "7772777", "initial_balance": 110, "account_number": '111111', "currency": "GBP"}' -H "Content-Type: application/json" -X POST http://localhost:5000/registration
```
###### ответ сервера:
```bash
{"details":"new user has been registered successfully"}
```

#### 2. Аутентификация пользователя
Аутентификация пользователя производится посредством POST запроса

###### пример запроса:
```bash
curl -d '{"email": "user_3@mail.ru", "password": "7772777"}' -H "Content-Type: application/json" -X POST http://localhost:5000/login
```
###### ответ сервера:
```bash
{"details":"successful authorization"}
```
#### 3. Перевод средств
Перевод средств производится посредством POST запроса
###### пример запроса:
```bash
curl -d '{"senders_account" : "111111", "receivers_account": "222222", "amount": 10}' -H "Content-Type: application/json" -X POST http://localhost:5000/transaction
```
###### ответ сервера:
```bash
{"details":"success"}
```

#### 4. Просмор списка всех операций по своему счету
Просмор списка операций по счету производится посредством GET запроса
###### пример запроса:
```bash
curl -X GET http://127.0.0.1:5000/statement/111111
```
###### ответ сервера:
```bash
{"transactions":{"2019-12-16-05.14.19":{"amount":"10","currency":"GBP","receivers_account":"222222","senders_account":"111111","type":"outcome"}}}
```


### Установка приложения 
```bash
git clone https://github.com/aquaracer/Exchange.git exchange_app
cd exchange_app
python3 -m venv env
./env/bin/activate
pip install -r requirements.txt
```
### Запуск сервиса
```bash
python3 app.py
```
### Запуск тестов
```bash
pytest test.py
```


