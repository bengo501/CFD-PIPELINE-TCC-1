@echo off
echo ========================================
echo   iniciando backend da api
echo ========================================
echo.
echo aguarde o uvicorn iniciar...
echo.
echo apos aparecer "Application startup complete."
echo o backend estara disponivel em:
echo   http://localhost:3000
echo   http://localhost:3000/docs (documentacao)
echo.
echo para parar, pressione CTRL+C
echo.
echo ========================================
python -m uvicorn app.main:app --reload --port 3000

