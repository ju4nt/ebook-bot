@echo off
echo Instalando dependencias EBook Bot...
pip install -r requirements.txt
echo.
echo Copiando .env.example a .env...
if not exist .env copy .env.example .env
echo.
echo Listo! Edita C:\ebook-bot\.env con tu ANTHROPIC_API_KEY
echo Luego ejecuta: python main.py
pause
