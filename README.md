# FastAPI Deal Management Service

Сервис управления сделками с авторизацией через VK ID на FastAPI.

## Структура проекта

```
app/
├── core/                  # Конфигурация и настройки
│   ├── __init__.py
│   ├── config.py         # Настройки приложения (БД, JWT, VK OAuth)
│   ├── database.py       # Подключение к БД
│   └── security.py       # Функции хеширования паролей
├── models/               # SQLAlchemy модели
│   ├── __init__.py
│   └── models.py         # Модели User, Deal, SharedDeal
├── schemas/              # Pydantic схемы
│   ├── __init__.py
│   ├── user.py           # Схемы для пользователей
│   └── deal.py           # Схемы для сделок
├── services/             # Бизнес-логика
│   ├── __init__.py
│   ├── auth_service.py   # JWT аутентификация
│   ├── vk_auth_service.py # VK OAuth авторизация
│   └── deal_service.py   # Операции со сделками
├── routers/              # API роутеры
│   ├── __init__.py
│   ├── auth_router.py    # Роуты авторизации
│   └── deal_router.py    # Роуты сделок
└── main.py               # Точка входа приложения
```

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Авторизация и аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/auth/vk/login` | Получить URL для авторизации через VK |
| POST | `/auth/vk/callback` | Обработка callback от VK |
| GET | `/auth/me` | Получить информацию о текущем пользователе |
| GET | `/auth/me/deals` | Получить все сделки пользователя |
| POST | `/auth/logout` | Выход из системы |

### Сделки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/deals/` | Создать новую сделку |
| GET | `/deals/` | Получить все сделки пользователя |
| GET | `/deals/{deal_id}` | Получить сделку по ID |
| PUT | `/deals/{deal_id}` | Обновить сделку |
| DELETE | `/deals/{deal_id}` | Удалить сделку |
| POST | `/deals/{deal_id}/share` | Поделиться ссылкой на сделку |
| POST | `/deals/{deal_id}/share-with-user` | Поделиться сделкой с пользователем |
| POST | `/deals/{deal_id}/upload-info` | Загрузить информацию о сделке |
| GET | `/deals/shared/{share_token}` | Получить сделку по токену (публично) |

## Настройка VK OAuth

1. Создайте приложение в [VK Developers](https://dev.vk.com/)
2. Получите `client_id` и `client_secret`
3. Укажите Redirect URI: `http://localhost:8000/auth/vk/callback`
4. Обновите настройки в `app/core/config.py`:

```python
VK_CLIENT_ID = "your_vk_client_id"
VK_CLIENT_SECRET = "your_vk_client_secret"
VK_REDIRECT_URI = "http://localhost:8000/auth/vk/callback"
```

## Документация API

После запуска сервера документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Пример использования

### 1. Авторизация через VK

```bash
# Получить URL для авторизации
curl http://localhost:8000/auth/vk/login

# После редиректа на VK и получения кода:
curl -X POST http://localhost:8000/auth/vk/callback \
  -H "Content-Type: application/json" \
  -d '{"code": "vk_auth_code"}'
```

### 2. Создание сделки

```bash
curl -X POST http://localhost:8000/deals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Сделка #1",
    "description": "Описание сделки",
    "amount": 100000
  }'
```

### 3. Поделиться ссылкой на сделку

```bash
curl -X POST http://localhost:8000/deals/1/share \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Получить сделку по публичной ссылке

```bash
curl http://localhost:8000/deals/shared/{share_token}
```

## Безопасность

- JWT токены используются для аутентификации
- Пароли хешируются с помощью bcrypt
- CORS настроен для развития (в продакшене ограничьте домены)
- Доступ к сделкам проверяется по владельцу или токену доступа
