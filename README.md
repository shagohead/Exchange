### Бэкенд.
Бэкенд реализован на Flask

### Базы данных
В качестве ORM используется sqlalchemy. 


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
