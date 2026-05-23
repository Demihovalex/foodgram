# Foodgram - продуктовый помощник

Foodgram — это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на других авторов, добавлять рецепты в избранное и формировать список покупок.

## Деплой

Проект доступен по адресу: [http://158.160.184.58:9000](http://158.160.184.58:9000)

Админ-панель: [http://158.160.184.58:9000/admin](http://158.160.184.58:9000/admin)

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
- Python 3.11 (для локальной разработки)

### Установка

# 1. Клонируйте репозиторий:
    bash
    git clone https://github.com/Demihovalex/foodgram.git
    cd foodgram

# 2. Создайте файл .env в корне проекта (на сервере):
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
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

# 3. Запустите контейнеры:
    cd infra
    docker compose -f docker-compose.production.yml up -d

# 4. Выполните миграции и соберите статику:
    docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput

# 5. Создайте суперпользователя:
    docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

# Деплой на сервер
    Проект развёрнут на сервере 158.160.184.58 с портом 9000.
    Для обновления проекта на сервере используется GitHub Actions. При пуше в ветку main автоматически:
    Собираются образы
    Загружаются на Docker Hub
    Обновляются контейнеры на сервере

# API
    Документация API доступна по адресу: http://158.160.184.58:9000/api/docs/

# Основные эндпоинты
    GET /api/recipes/ Список рецептов
    POST /api/recipes/ Создание рецепта
    GET /api/tags/ Список тегов
    GET /api/ingredients/ Список ингредиентов
    POST /api/auth/token/login/ Получение токена
    POST /api/auth/users/ Регистрация пользователя
    GET /api/users/me/ Информация о текущем пользователе
    POST /api/recipes/{id}/favorite/ Добавить рецепт в избранное
    POST /api/recipes/{id}/shopping_cart/ Добавить рецепт в список покупок
    GET /api/recipes/download_shopping_cart/ Скачать список покупок

# Админка
    Админ-панель доступна по адресу: http://158.160.184.58:9000/admin

# Автор
# Aлександр Демихов
