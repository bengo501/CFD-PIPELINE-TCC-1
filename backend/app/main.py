# ponto de entrada fastapi do pipeline cfd
# expoe rotas http monta estaticos e liga routers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

# pasta raiz do repositorio tres niveis acima deste ficheiro
project_root = Path(__file__).parent.parent.parent
# permite imports tipo backend app a partir da raiz
sys.path.insert(0, str(project_root))

from backend.app.api import routes
from backend.app.database.connection import DatabaseConnection
from backend.app.database.seed_demo import seed_demo_data_if_needed

# instancia principal da api documentacao em docs e redoc
app = FastAPI(
    title="CFD Pipeline API",
    description="api rest para gerenciar pipeline de simulações cfd de leitos empacotados",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# cors permite browser em localhost3000 ou 5173 chamar a api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # vite usa 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pasta onde ficam artefactos gerados servidos tambem em url files
output_dir = project_root / "generated"
output_dir.mkdir(exist_ok=True)

app.mount("/files", StaticFiles(directory=str(output_dir)), name="files")

# rotas genericas compilacao modelo jobs ficheiros
app.include_router(routes.router, prefix="/api")

# crud sql beds simulations results dashboard
from backend.app.api import routes_database
app.include_router(routes_database.router, prefix="/api")

# pipeline assincrono completo
from backend.app.api import routes_integrated
app.include_router(routes_integrated.router, prefix="/api")

# wizard web cfd casos templates
from backend.app.api import routes_wizard, routes_cfd, routes_casos, routes_templates
app.include_router(routes_wizard.router, prefix="/api")
app.include_router(routes_cfd.router, prefix="/api")
app.include_router(routes_casos.router, prefix="/api")
app.include_router(routes_templates.router, prefix="/api")

from backend.app.api import routes_reports
app.include_router(routes_reports.router, prefix="/api")

from backend.app.api import routes_profile
app.include_router(routes_profile.router, prefix="/api")

from backend.app.api import routes_settings
app.include_router(routes_settings.router, prefix="/api")

from backend.app.api import routes_admin
app.include_router(routes_admin.router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    # ao arrancar cria tabelas se faltarem
    DatabaseConnection.create_tables()
    # opcionalmente insere linhas demo conforme env
    seed_demo_data_if_needed()


@app.get("/")
async def root():
    # resposta minima para saber que o servico esta de pe
    return {
        "message": "cfd pipeline api",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health():
    # testa ligacao ao motor sql para o painel de estado
    db_status = DatabaseConnection.check_connection()

    return {
        "status": "healthy" if db_status else "degraded",
        "services": {
            "bed_compiler": "available",
            "blender": "available",
            "openfoam": "available",
            "database": "connected" if db_status else "disconnected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # modo reload util em desenvolvimento local
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # hot reload em desenvolvimento
        log_level="info"
    )
