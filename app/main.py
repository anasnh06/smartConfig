from fastapi import FastAPI
from app.api.v1.endpoints import users, auth, roles, os, environments, projects, servers, configurations, templates, template_configurations, server_templates, server_configurations, execution_groups, executions
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.app_name, debug=True)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(os.router, prefix="/api/v1/operating-systems", tags=["Operating Systems"])
app.include_router(environments.router, prefix="/api/v1/environments", tags=["Environments"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(servers.router, prefix="/api/v1/servers", tags=["Servers"])
app.include_router(configurations.router, prefix="/api/v1/configurations", tags=["Configurations"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Templates"])
app.include_router(template_configurations.router, prefix="/api/v1/template-configurations", tags=["Template Configurations"])
app.include_router(server_templates.router, prefix="/api/v1/server-templates", tags=["Server Templates"])
app.include_router(server_configurations.router, prefix="/api/v1/server-configurations", tags=["Server Configurations"])
app.include_router(execution_groups.router, prefix="/api/v1/execution-groups", tags=["Execution Groups"])
app.include_router(executions.router, prefix="/api/v1/executions", tags=["Executions"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 👈 Ajoute aussi ton domaine Vercel en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

