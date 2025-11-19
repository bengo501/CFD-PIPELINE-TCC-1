@echo off
echo ========================================
echo   CONJUNTO G4 - TESTES AUTOMATIZADOS
echo ========================================
echo.

cd /d %~dp0

echo [1/3] Verificando backend...
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% neq 0 (
    curl -s http://localhost:8000/health >nul 2>&1
    if %errorlevel% neq 0 (
        curl -s http://localhost:8000/api/status >nul 2>&1
        if %errorlevel% neq 0 (
            echo   ERRO: Backend nao esta respondendo!
            echo   Inicie o backend antes de executar os testes.
            echo   Execute: cd ..\..\backend ^&^& EXECUTAR.bat
            pause
            exit /b 1
        )
    )
)
echo   OK: Backend esta online
echo.

echo [2/3] Executando testes G4...
echo.

python test_g4_simplified.py

if %errorlevel% neq 0 (
    echo.
    echo   AVISO: Alguns testes podem ter falhado.
    echo   Verifique os logs em results\g4_report.txt
) else (
    echo.
    echo   OK: Testes concluidos!
)

echo.
echo [3/3] Resultados salvos em:
echo   - results\g4_metrics.csv
echo   - results\g4_report.txt
echo   - results\runs\<hash>\
echo.

pause

