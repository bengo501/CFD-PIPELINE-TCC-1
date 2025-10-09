"""
backend fastapi para pipeline cfd
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

# adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.api import routes

# criar app fastapi
app = FastAPI(
    title="CFD Pipeline API",
    description="api rest para gerenciar pipeline de simulações cfd de leitos empacotados",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# configurar cors (desenvolvimento)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # vite usa 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# montar pasta de arquivos estáticos
output_dir = project_root / "output"
output_dir.mkdir(exist_ok=True)

app.mount("/files", StaticFiles(directory=str(output_dir)), name="files")

# incluir rotas
app.include_router(routes.router, prefix="/api")

# rota raiz
@app.get("/")
async def root():
    """endpoint raiz"""
    return {
        "message": "cfd pipeline api",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }

# rota de health check
@app.get("/health")
async def health():
    """verifica saúde do serviço"""
    return {
        "status": "healthy",
        "services": {
            "bed_compiler": "available",
            "blender": "available",
            "openfoam": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # hot reload em desenvolvimento
        log_level="info"
    )

