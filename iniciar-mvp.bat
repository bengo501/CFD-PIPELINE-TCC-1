@echo off
echo ========================================
echo   CFD PIPELINE - MVP LOCAL
echo ========================================
echo.

echo [verificacao] verificando dependencias...

REM verificar python
python --version >nul 2>&1
if errorlevel 1 (
    echo erro: python nao encontrado!
    echo instale python 3.11+
    pause
    exit /b 1
)
echo python encontrado ✓

REM verificar node
node --version >nul 2>&1
if errorlevel 1 (
    echo erro: node.js nao encontrado!
    echo instale node.js 18+
    pause
    exit /b 1
)
echo node.js encontrado ✓

echo.
echo [setup] escolha uma opcao:
echo.
echo 1. iniciar backend apenas
echo 2. iniciar frontend apenas
echo 3. iniciar backend + frontend
echo 4. testar api
echo 5. abrir documentacao swagger
echo 6. verificar banco de dados
echo.
set /p choice="escolha (1-6): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
if "%choice%"=="4" goto test_api
if "%choice%"=="5" goto docs
if "%choice%"=="6" goto check_db

:backend
echo.
echo [backend] iniciando servidor fastapi...
echo.
cd backend
python -m uvicorn app.main:app --reload
goto end

:frontend
echo.
echo [frontend] iniciando react dev server...
echo.
cd frontend
npm run dev
goto end

:both
echo.
echo [backend] iniciando servidor fastapi em nova janela...
start "CFD Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload"
timeout /t 3 >nul

echo.
echo [frontend] iniciando react dev server...
cd frontend
npm run dev
goto end

:test_api
echo.
echo [teste] testando api...
echo.
curl http://localhost:8000/health
echo.
echo.
curl http://localhost:8000/
echo.
pause
goto end

:docs
echo.
echo [docs] abrindo documentacao swagger...
start http://localhost:8000/docs
echo.
echo acesse: http://localhost:8000/docs
pause
goto end

:check_db
echo.
echo [database] verificando banco de dados...
echo.
cd backend
python -c "from app.database.connection import check_connection; print('status:', 'conectado' if check_connection() else 'desconectado')"
echo.
pause
goto end

:end
echo.
echo ========================================
echo   SERVICOS DISPONIVEIS:
echo ========================================
echo.
echo frontend:    http://localhost:5173
echo backend:     http://localhost:8000
echo docs api:    http://localhost:8000/docs
echo health:      http://localhost:8000/health
echo.
pause
