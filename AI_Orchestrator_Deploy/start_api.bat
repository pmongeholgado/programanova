@echo off
title AI ORCHESTRATOR - Servidor API
echo Iniciando entorno virtual...
call .venv\Scripts\activate.bat

echo Lanzando API...
python api_server.py

pause
