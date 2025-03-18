[![Main workflow](https://github.com/StasChernov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/StasChernov/foodgram/actions/workflows/main.yml)

#  Foodgram

Foodgram - сервис для публикации рецептов.
В данном сервисе пользователи могут делиться рецептами.
Сервис доступен по адресу [Foodgram](https://chefoodgram.zapto.org)

## Используемые технологии

- ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) Python
- ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) Docker
- ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) Nginx
- ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) Rect
- ![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white) PostgreSQL


## Запуск проекта на сервере

1. Настроить Nginx:

   Необходимо сконфигурировать Nginx так, что бы все запросы перенапралялить в контейтен на порт 9000.
   
   Перезапустить Nginx.

   ```bash
   sudo systemctl restart nginx
   ```

2. В корневую директорию проекта скопируйте файл .env предваретельно заполнив следующие данные:
    ``` bash
    POSTGRES_USER = владелец базы
    POSTGRES_PASSWORD = пароль базы
    POSTGRES_DB = имя базы
    DB_HOST = db
    DB_PORT = 5432
    SECRET_KEY = секретный ключ приложения django
    ALLOWED_HOSTS = разрешенные хосты
    DEBUG = состояние режима отладки
    ```        

3. Запушить внесенные изменения на GitHub.

## Автор проекта
[Станислав Чернов](https://github.com/StasChernov)
