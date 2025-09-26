@echo off
echo ========================================
echo   EXECUTOR DE LEITO HEADLESS
echo ========================================
echo.

echo procurando blender...
where blender >nul 2>&1
if %errorlevel% neq 0 (
    echo erro: blender nao encontrado no path
    echo instale o blender ou adicione ao path do sistema
    pause
    exit /b 1
)

echo blender encontrado!
echo.

echo executando leito_extracao.py...
blender --background --python "..\blender_scripts\leito_extracao.py"

if %errorlevel% equ 0 (
    echo.
    echo sucesso! leito criado.
) else (
    echo.
    echo erro na execucao!
)

echo.
pause
