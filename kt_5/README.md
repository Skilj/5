- conftest.py — будет использован для написания фикстур
- requirements.txt — для установки необходимых модулей в контейнере с python

**Создание окружения**

1. Через командную строку с помощью следующей команды создаем окружение: <br>`python -m venv venv`
2. Далее для Windows активируем окружение: <br>`.\venv\Scripts\activate`
3. После этого устанавливаем зависимости в окружение: <br>`pip install -r .\requirements.txt`

**Tests**
1. `python -m pytest --alluredir=./allure-results`
2. `allure serve` <br> or `allure generate`