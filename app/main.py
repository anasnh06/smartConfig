from fastapi import FastAPI
from app.api.v1.endpoints import users, auth, roles, os, environments, projects, servers, configurations
from app.core.config import settings

app = FastAPI(title=settings.app_name)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(os.router, prefix="/api/v1/operating-systems", tags=["Operating Systems"])
app.include_router(environments.router, prefix="/api/v1/environments", tags=["Environments"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(servers.router, prefix="/api/v1/servers", tags=["Servers"])
app.include_router(configurations.router, prefix="/api/v1/configurations", tags=["Configurations"])

