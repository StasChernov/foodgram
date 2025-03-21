[![Main workflow](https://github.com/StasChernov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/StasChernov/foodgram/actions/workflows/main.yml)

#  Foodgram

Foodgram - сервис для публикации рецептов.
В данном сервисе пользователи могут делиться рецептами.
Сервис доступен по адресу [Foodgram](https://chefoodgram.zapto.org)

## Используемые технологии

![Django](https://img.shields.io/badge/Django-%23092E20.svg?logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?logo=sqlite&logoColor=white)
![Django](https://img.shields.io/badge/Django-%23092E20.svg?logo=django&logoColor=white)

- Python
- Docker
- Nginx
- React
- PostgreSQL
- SQLite
- Django

## Запуск проекта

1. Склонируйте репозиторий себе на компьютер.

```bash
git clone https://github.com/StasChernov/foodgram.git
```

2. Перейдите в папку с проектом

```bash
cd foodgram
```

3. Создайте файл с переменными окружения .env содержащий следующие пункты:

``` bash
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
SECRET_KEY
DB_HOST
DB_PORT
DEBUG
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
```

4. Для запуска введите комманду:

```bash
docker compose up -d
```

5. Выполните миграции:

```bash
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

6. Соберите статику:

```bash
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/static/
```

7. Заполните таблицы Ingredient и Tag:

```bash
docker compose -f docker-compose.yml exec backend python manage.py load_json_ingredients
docker compose -f docker-compose.yml exec backend python manage.py load_json_tags
```

## Локальный запуск проекта без Docker
1. Склонируйте репозиторий себе на компьютер.

```bash
git clone https://github.com/StasChernov/foodgram.git
```

2. Перейдите в папку с проектом

```bash
cd foodgram
```
3. Создайте файл с переменными окружения .env содержащий следующие пункты:

``` bash
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
SECRET_KEY
DB_HOST
DB_PORT
DEBUG
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
```

4. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/Scripts/activate
``` 

5. Устанавите зависимости:

```bash
pip install -r backend/requirements.txt
```

6. В папке backend/foodgram выполните миграции:

```bash
python manage.py migrate
```

7. Заполните таблицы Ingredient и Tag:

```bash
python manage.py load_json_ingredients
python manage.py load_json_tags
```

8. Запустите проект:

```bash
python manage.py runserver
```

9. Ссылки:

После запуска проекта будут доступны следующие ссылки:

[Админка](http://127.0.0.1:8000/admin/)
[API](http://127.0.0.1:8000/api/)

## Доступ к документации по API

Перейдите в папку infra репозитория, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу [Фронтенд](http://localhost) изучите фронтенд веб-приложения, а по адресу [Docs](http://localhost/api/docs/) — спецификацию API.

## Автор проекта
[Станислав Чернов](https://github.com/StasChernov)
