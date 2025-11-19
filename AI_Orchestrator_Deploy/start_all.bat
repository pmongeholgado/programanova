@echo off
title AI ORCHESTRATOR - Full Start
echo ============================================
echo     INICIANDO PROGRAMA NOVA COMPLETO
echo ============================================
echo.

REM ---- 1) Activar entorno virtual ----
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.

REM ---- 2) Iniciar API en una ventana separada ----
echo Lanzando API del Orchestrator...
start cmd /k "python api_server.py"

timeout /t 3 >nul

REM ---- 3) Iniciar NGROK en otra ventana ----
echo Iniciando Ngrok...
start cmd /k "ngrok http 8000"

timeout /t 3 >nul

REM ---- 4) Iniciar Frontend ----
echo Lanzando Frontend...
start cmd /k "python -m http.server 8081 --directory frontend"

echo.
echo ============================================
echo  Todo lanzado correctamente 🎉
echo  API:        http://localhost:8000
echo  FRONTEND:   http://localhost:8081
echo ============================================
echo.

pause
