@echo off
chcp 65001 > nul
title Test & Certificate Bot

echo.
echo ========================================
echo 🤖 Test ^& Certificate Bot
echo ========================================
echo.

REM .env faylini tekshirish
if not exist .env (
    echo ❌ .env fayli topilmadi!
    echo.
    echo 1. .env.example dan nusxa oling:
    echo    copy .env.example .env
    echo.
    echo 2. .env faylini tahrirlang:
    echo    notepad .env
    echo.
    pause
    exit /b 1
)

REM Python versiyasini tekshirish
echo 🐍 Python versiyasi:
python --version
echo.

REM Virtual environment tekshirish
if exist venv (
    echo ✅ Virtual environment topildi
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment yo'q
    set /p create_venv="Yaratishni xohlaysizmi? (y/n): "
    if /i "%create_venv%"=="y" (
        python -m venv venv
        call venv\Scripts\activate.bat
        echo ✅ Virtual environment yaratildi
    )
)

REM Requirements o'rnatish
echo.
echo 📦 Kutubxonalarni tekshirish...
pip install -r requirements.txt -q

REM Papkalarni yaratish
echo.
echo 📁 Papkalarni tekshirish...
if not exist certificates mkdir certificates
if not exist templates mkdir templates
if not exist fonts mkdir fonts
if not exist logs mkdir logs

REM Konfiguratsiyani tekshirish
echo.
python config.py
if errorlevel 1 (
    echo ❌ Konfiguratsiya xato!
    pause
    exit /b 1
)

REM Sertifikat shablonini tekshirish
if not exist templates\certificate_template.png (
    echo.
    echo ⚠️  Sertifikat shabloni topilmadi
    set /p create_template="Yangi shablon yaratish? (y/n): "
    if /i "%create_template%"=="y" (
        python create_template.py
    )
)

REM Botni ishga tushirish
echo.
echo ========================================
echo 🚀 Bot ishga tushmoqda...
echo Ctrl+C - to'xtatish
echo ========================================
echo.

python bot.py

pause
