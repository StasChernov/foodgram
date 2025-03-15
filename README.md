[![Main workflow](https://github.com/StasChernov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/StasChernov/foodgram/actions/workflows/main.yml)

#  Foodgram

Foodgram - сервис для публикации рецептов.
В данном сервисе пользователи могут делиться рецептами.

Приложение доступно по адресу: https:\\chefoodgram.zapto.org

## Используемые технологии

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

## Запуск проекта на сервере

1. Установить docker compose на сервер:
    ```bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt install docker-compose-plugin
    ```

2. Настроить Nginx:

   Необходимо сконфигурировать Nginx так, что бы все запросы перенапралялить в контейтен на порт 9000.
   
   Перезапустить Nginx.

   ```bash
   sudo systemctl restart nginx
   ```

3. В корневую директорию проекта скопируйте файл .env предваретельно заполнив следующие данные:
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

4. Запушить внесенные изменения на GitHub.

## Автор проекта
[Станислав Чернов](https://github.com/StasChernov)
