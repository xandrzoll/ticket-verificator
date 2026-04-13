from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.core.database import Base, engine
from app.routers import auth_router, deal_router

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Локатор Билетов",
    description="Сервис управления сделками с авторизацией через VK ID",
    version="1.0.0"
)

# Настройка шаблонов
templates = Jinja2Templates(directory="app/templates")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(deal_router)


@app.get("/")
async def root(request: Request):
    """
    Главная страница сайта
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Проверка здоровья сервиса
    """
    return {"status": "healthy"}
