@echo off
title AI ORCHESTRATOR - Frontend
echo Iniciando servidor web para el frontend...

cd frontend
python -m http.server 8081

pause
