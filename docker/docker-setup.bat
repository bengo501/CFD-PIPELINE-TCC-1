@echo off
echo ========================================
echo   CFD PIPELINE - DOCKER SETUP
echo ========================================
echo.

echo [1/5] verificando docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo erro: docker nao encontrado!
    echo instale docker desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo docker encontrado ✓

echo.
echo [2/5] verificando docker-compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo erro: docker-compose nao encontrado!
    pause
    exit /b 1
)
echo docker-compose encontrado ✓

echo.
echo [3/5] criando arquivo .env...
if not exist .env (
    copy env.example .env
    echo arquivo .env criado ✓
) else (
    echo arquivo .env ja existe ✓
)

echo.
echo [4/5] parando containers existentes...
docker-compose down

echo.
echo [5/5] iniciando containers...
docker-compose up -d

echo.
echo ========================================
echo   CONTAINERS INICIADOS!
echo ========================================
echo.
echo servicos disponiveis:
echo - frontend:    http://localhost:5173
echo - backend:     http://localhost:8000
echo - postgres:    localhost:5432
echo - redis:       localhost:6379
echo - minio:       http://localhost:9000
echo - minio admin: http://localhost:9001
echo.
echo para ver logs: docker-compose logs -f
echo para parar:    docker-compose down
echo.
pause
