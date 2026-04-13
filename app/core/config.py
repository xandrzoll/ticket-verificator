# Database configuration
DATABASE_URL = "sqlite:///./app.db"

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# VK OAuth settings
VK_CLIENT_ID = "your_vk_client_id"
VK_CLIENT_SECRET = "your_vk_client_secret"
VK_REDIRECT_URI = "http://localhost:8000/auth/vk/callback"
