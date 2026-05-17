# Foodgram - продуктовый помощник

Foodgram — это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на других авторов, добавлять рецепты в избранное и формировать список покупок.

## Технологии

- Python 3.11
- Django 5.1
- Django REST Framework
- Djoser (аутентификация по токенам)
- PostgreSQL
- Docker / Docker Compose
- GitHub Actions (CI/CD)
- Nginx

## Как развернуть проект

### Требования

- Docker и Docker Compose на сервере
- Домен или IP-адрес

### Установка

# 1. Клонируйте репозиторий:
    bash
    git clone https://github.com/Demihovalex/foodgram.git
    cd foodgram

# 2. Создайте файл .env в корне проекта (на сервере):
    env
    POSTGRES_DB=foodgram_db
    POSTGRES_USER=foodgram_user
    POSTGRES_PASSWORD=foodgram_password
    DB_NAME=foodgram_db
    DB_USER=foodgram_user
    DB_PASSWORD=foodgram_password
    DB_HOST=db
    DB_PORT=5432
    DB_ENGINE=postgresql
    SECRET_KEY=ваш_секретный_ключ
    DEBUG=False
    ALLOWED_HOSTS=ваш_IP_или_домен

# 3. Запустите контейнеры:
    bash
    cd infra
    docker compose -f docker-compose.production.yml up -d

# 4. Выполните миграции и соберите статику:
    bash
    docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput

# 5. Создайте суперпользователя:
    bash
    docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
# API
    Документация API доступна по адресу: http://ваш-IP/api/docs/

# Основные эндпоинты
    GET /api/recipes/ — список рецептов
    POST /api/recipes/ — создание рецепта
    GET /api/tags/ — список тегов
    GET /api/ingredients/ — список ингредиентов
    POST /api/auth/token/login/ — получение токена
    POST /api/auth/users/ — регистрация пользователя
    GET /api/users/me/ — информация о текущем пользователе
    POST /api/recipes/{id}/favorite/ — добавить рецепт в избранное
    POST /api/recipes/{id}/shopping_cart/ — добавить рецепт в список покупок
    GET /api/recipes/download_shopping_cart/ — скачать список покупок

# Админка
    Админ-панель доступна по адресу: http://ваш-IP/admin/

# Автор
# Aлександр Демихов
