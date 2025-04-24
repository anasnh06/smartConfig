from fastapi import FastAPI
from app.api.v1.endpoints import users, auth
from app.core.config import settings

app = FastAPI(title=settings.app_name)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
