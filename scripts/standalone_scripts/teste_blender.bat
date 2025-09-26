@echo off
echo testando blender...
blender --version
echo.
echo executando leito_extracao.py...
blender --background --python "..\blender_scripts\leito_extracao.py"
echo.
echo fim do teste
pause
