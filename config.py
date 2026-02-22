#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Configuration File
Barcha sozlamalar va konstantalar
"""

import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# ========== BOT SOZLAMALARI ==========

# Bot Token - @BotFather dan olingan
BOT_TOKEN = os.getenv('BOT_TOKEN', '8153737070:AAECwrqAsh7AsuLnKwOApx7FsWc5XIwkLZ8')

# Kanal username - obuna majburiy
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@TeacherRahmatjon_math')

# Admin ID lar - vergul bilan ajratilgan
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '5678712917')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip().isdigit()]

# ========== PAPKA SOZLAMALARI ==========

# Sertifikatlar saqlanadigan papka
CERTIFICATES_DIR = 'certificates'

# Sertifikat shablonlari papkasi
TEMPLATES_DIR = 'templates'

# Fontlar papkasi
FONTS_DIR = 'fonts'

# Loglar papkasi
LOGS_DIR = 'logs'

# ========== DATABASE SOZLAMALARI ==========

# Database fayl yo'li
DATABASE_PATH = 'bot.db'

# ========== PAPKALARNI YARATISH ==========

# Barcha kerakli papkalarni yaratish
for directory in [CERTIFICATES_DIR, TEMPLATES_DIR, FONTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# ========== SOZLAMALARNI TEKSHIRISH ==========

def check_config():
    """Sozlamalarni tekshirish"""
    errors = []
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        errors.append("❌ BOT_TOKEN .env faylida to'ldirilmagan!")
    
    if not CHANNEL_USERNAME.startswith('@'):
        errors.append("❌ CHANNEL_USERNAME @ belgisi bilan boshlanishi kerak!")
    
    if not ADMIN_IDS:
        errors.append("⚠️ ADMIN_IDS bo'sh - admin funksiyalari ishlamaydi!")
    
    if errors:
        print("\n" + "="*50)
        print("🚨 KONFIGURATSIYA XATOLARI:")
        print("="*50)
        for error in errors:
            print(error)
        print("="*50 + "\n")
        print("📝 .env faylini to'g'ri to'ldiring!\n")
        return False
    
    print("\n" + "="*50)
    print("✅ KONFIGURATSIYA TO'G'RI!")
    print("="*50)
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"📢 Kanal: {CHANNEL_USERNAME}")
    print(f"👑 Adminlar soni: {len(ADMIN_IDS)}")
    print(f"📁 Papkalar: OK")
    print("="*50 + "\n")
    return True

if __name__ == '__main__':
    check_config()
