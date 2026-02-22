#!/bin/bash

echo "🤖 Test & Certificate Bot"
echo "=========================="
echo ""

# Rangli output uchun
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# .env faylini tekshirish
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env fayli topilmadi!${NC}"
    echo ""
    echo "1. .env.example dan nusxa oling:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. .env faylini tahrirlang:"
    echo "   nano .env"
    echo ""
    exit 1
fi

# Python versiyasini tekshirish
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}🐍 Python versiya: $python_version${NC}"

# Virtual environment borligini tekshirish
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment topildi${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Virtual environment yo'q${NC}"
    read -p "Yaratishni xohlaysizmi? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment yaratildi${NC}"
    fi
fi

# Requirements o'rnatish
echo -e "${YELLOW}📦 Kutubxonalarni tekshirish...${NC}"
pip install -r requirements.txt -q

# Papkalarni yaratish
echo -e "${YELLOW}📁 Papkalarni tekshirish...${NC}"
mkdir -p certificates templates fonts logs

# Konfiguratsiyani tekshirish
echo ""
python3 config.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Konfiguratsiya xato!${NC}"
    exit 1
fi

# Sertifikat shablonini tekshirish
if [ ! -f "templates/certificate_template.png" ]; then
    echo -e "${YELLOW}⚠️  Sertifikat shabloni topilmadi${NC}"
    read -p "Yangi shablon yaratish? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 create_template.py
    fi
fi

# Botni ishga tushirish
echo ""
echo -e "${GREEN}🚀 Bot ishga tushmoqda...${NC}"
echo "Ctrl+C - to'xtatish"
echo ""

python3 bot.py
