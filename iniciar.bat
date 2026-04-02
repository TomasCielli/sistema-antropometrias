@echo off
title Albatros Rugby Club - Antropometrias

echo.
echo  ==========================================
echo   Albatros Rugby Club - Antropometrias
echo  ==========================================
echo.

:: Ir al directorio del script
cd /d "%~dp0"

:: Verificar que Python esta disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no esta instalado o no esta en el PATH.
    echo  Instala Python desde https://www.python.org
    pause
    exit /b 1
)

:: Instalar dependencias si faltan
echo  Verificando dependencias...
pip install flask openpyxl --quiet

echo.
echo  Iniciando el servidor...
echo  Accede desde cualquier dispositivo en la misma red:
echo.

:: Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
    set IP=%%a
)
set IP=%IP: =%

echo    Esta computadora:  http://localhost:5000
echo    iPad / celular:    http://%IP%:5000
echo.
echo  Presiona Ctrl+C para detener el servidor.
echo  ==========================================
echo.

:: Abrir el navegador despues de 2 segundos
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Iniciar Flask
python app.py

pause
