### Описание проекта:

Yatube - социальная сеть для публикации личных дневников.
Python 3.7, Django 2.2, PostgreSQL, gunicorn, nginx, Yandex Cloud (Ubuntu 20.04 lts), GIT.
Проект разработан по MVT архитектуре. Используются декораторы и пагинация постов. Создана система подписки и кэширование. Реализовано тестирование проекта с помощью библиотеки Unittest.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:ifyoumasha/hw05_final.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
или
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
или
python manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
или
python manage.py runserver
```

Перейти на главную страницу проекта:

```
http://127.0.0.1:8000/
```
