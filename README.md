# 🤖 Professional Test & Certificate Bot

**Test tekshirish va avtomatik sertifikat beruvchi Telegram bot**

---

## ✨ XUSUSIYATLAR

✅ **Majburiy obuna tizimi** - Kanalga obuna bo'lmasdan botdan foydalanib bo'lmaydi  
✅ **Bir martalik registratsiya** - Foydalanuvchi bir marta ism-familiyasini kiritadi  
✅ **Test format validatsiyasi** - Format: `505*abcdabcd...`  
✅ **Avtomatik tekshirish** - To'g'ri/noto'g'ri javoblarni hisoblash  
✅ **70% sertifikat** - 70% va undan yuqori ballda avtomatik sertifikat  
✅ **Bir test = 1 sertifikat** - Qayta yechishda sertifikat berilmaydi  
✅ **Admin panel** - Yangi test qo'shish, statistika, broadcast  
✅ **Excel statistika** - Barcha natijalarni Excel faylda yuklab olish  

---

## 📦 O'RNATISH

### 1. Kerakli dasturlar

```bash
# Python 3.8 yoki yuqori versiya
python3 --version

# pip package manager
pip3 --version
```

### 2. Loyihani yuklab olish

```bash
# GitHub dan clone qilish (agar repodan olingan bo'lsa)
git clone https://github.com/username/test_bot.git
cd test_bot

# Yoki ZIP arxivni ochish
unzip test_bot.zip
cd test_bot
```

### 3. Virtual environment yaratish (tavsiya etiladi)

```bash
# Virtual environment yaratish
python3 -m venv venv

# Aktivlashtirish
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 5. .env faylini sozlash

```bash
# .env.example dan nusxa oling
cp .env.example .env

# .env faylini tahrirlang
nano .env  # yoki istalgan text editor
```

**.env fayl tarkibi:**

```env
BOT_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
CHANNEL_USERNAME=@TeacherRahmatjon_math
ADMIN_IDS=123456789,987654321
```

**Qanday to'ldirish kerak:**

1. **BOT_TOKEN** - Telegram @BotFather ga o'tib:
   - `/start` yuboring
   - `/newbot` yuboring
   - Bot nomini kiriting (masalan: `My Test Bot`)
   - Bot username kiriting (masalan: `my_test_bot`)
   - Token ni nusxalang va .env ga qo'ying

2. **CHANNEL_USERNAME** - O'z kanalingiz username ini yozing (@ bilan)

3. **ADMIN_IDS** - O'z Telegram ID ingizni oling:
   - @userinfobot ga `/start` yuboring
   - ID ni nusxalang
   - Bir nechta admin bo'lsa vergul bilan ajrating: `123456789,987654321`

### 6. Sertifikat shablonini yaratish

```bash
# Oddiy shablon avtomatik yaratish
python3 create_template.py
```

Yoki o'zingiz Photoshop/Canva da yaratib `templates/` papkasiga joylashtiring.

### 7. Konfiguratsiyani tekshirish

```bash
python3 config.py
```

Agar hammasi to'g'ri bo'lsa, shunday xabar chiqadi:
```
✅ KONFIGURATSIYA TO'G'RI!
🤖 Bot Token: 7123456789...Dsaw
📢 Kanal: @TeacherRahmatjon_math
👑 Adminlar soni: 2
📁 Papkalar: OK
```

---

## 🚀 ISHGA TUSHIRISH

### Linux/Mac:

```bash
python3 bot.py
```

### Windows:

```bash
python bot.py
```

### Yoki avtomatik skript:

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

---

## 📖 FOYDALANISH

### Oddiy foydalanuvchi:

1. **Botni boshlash:**
   - `/start` yuboring
   - Kanalga obuna bo'ling
   - "✅ Obunani tekshirish" ni bosing

2. **Ro'yxatdan o'tish:**
   - Ism-familiyangizni kiriting: `Rahmatjon Ergashev`

3. **Test yechish:**
   - Format: `[TestID]*[javoblar]`
   - Namuna: `505*aabcdcbadcbaabc`
   - Javoblar: faqat `a, b, c, d` harflari

4. **Natijani ko'rish:**
   - `/myresults` - o'z natijalaringiz

5. **Yordam:**
   - `/help` - to'liq qo'llanma

### Admin:

1. **Yangi test qo'shish:**
   ```
   /newtest
   → Test ID: 505
   → Kalitlar: aabcdcbadcbaabc
   → Sertifikat shablonini yuklang
   ```

2. **Statistika:**
   ```
   /stat
   → Umumiy statistika
   → Excel fayl yuklab olish
   ```

3. **Xabar yuborish:**
   ```
   /broadcast
   → Xabaringizni yozing
   → Tasdiqlang
   → Barcha foydalanuvchilarga yuboriladi
   ```

---

## 📁 PAPKA STRUKTURASI

```
test_bot/
├── bot.py                  # Asosiy bot kodi
├── database.py             # Database funksiyalari
├── certificate_gen.py      # Sertifikat generatori
├── config.py               # Konfiguratsiya
├── create_template.py      # Shablon yaratish
├── requirements.txt        # Python kutubxonalar
├── .env                    # Sozlamalar (maxfiy)
├── .env.example            # Sozlamalar namunasi
├── README.md               # Dokumentatsiya
├── bot.db                  # SQLite database
├── certificates/           # Yaratilgan sertifikatlar
├── templates/              # Sertifikat shablonlari
│   └── certificate_template.png
├── fonts/                  # Fontlar (Arial.ttf)
└── logs/                   # Log fayllari
    └── bot.log
```

---

## 🔧 SOZLAMALAR

### 1. Test format

- **Format:** `[TestID]*[javoblar]`
- **TestID:** 3 xonali raqam (masalan: `505`)
- **Javoblar:** faqat `a, b, c, d` harflari
- **Uzunlik:** 10-100 ta savol
- **Namuna:** `505*aabcdcbadcbaabc`

### 2. Sertifikat olish

- **Minimal ball:** 70%
- **Bir test = 1 sertifikat**
- **Qayta yechish:** Ruxsat beriladi, lekin sertifikat faqat birinchi marta

### 3. Admin huquqlari

`.env` faylida `ADMIN_IDS` ga qo'shilgan foydalanuvchilar:
- Yangi test qo'sha oladi
- Statistika ko'ra oladi
- Broadcast xabar yubora oladi

---

## 🐛 MUAMMOLARNI HAL QILISH

### Bot ishlamayapti?

1. **Token xato:**
   ```bash
   # .env faylni tekshiring
   cat .env
   
   # Tokenni yangilang
   nano .env
   ```

2. **Obuna tekshirilmayapti:**
   - Botni kanalga admin qiling
   - Kanal username to'g'ri ekanligini tekshiring

3. **Sertifikat yaratilmayapti:**
   ```bash
   # Shablon borligini tekshiring
   ls templates/
   
   # Yangi shablon yarating
   python3 create_template.py
   ```

4. **Database xatosi:**
   ```bash
   # Database ni qayta yaratish
   rm bot.db
   python3 bot.py
   ```

### Log faylni ko'rish

```bash
# So'nggi 50 qator
tail -n 50 logs/bot.log

# Real-time monitoring
tail -f logs/bot.log
```

---

## 🌐 HOSTINGGA JOYLASHTIRISH

### PythonAnywhere (BEPUL):

1. [pythonanywhere.com](https://www.pythonanywhere.com) da ro'yxatdan o'ting
2. Console ochib:
   ```bash
   git clone your_repo_url
   cd test_bot
   pip3 install --user -r requirements.txt
   ```
3. `.env` faylini yarating
4. **Files** → **Always on tasks** → `python3 bot.py`

### Heroku:

```bash
# Procfile yarating
echo "worker: python bot.py" > Procfile

# runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create your-bot-name
git push heroku main
heroku ps:scale worker=1
```

### VPS (Digital Ocean, AWS, etc):

```bash
# Server ga ulanish
ssh user@your-server-ip

# Loyihani ko'chirish
git clone your_repo_url
cd test_bot

# O'rnatish
pip3 install -r requirements.txt

# .env sozlash
nano .env

# Screen da ishga tushirish
screen -S testbot
python3 bot.py

# Screen dan chiqish: Ctrl+A, D
# Qayta kirish: screen -r testbot
```

---

## 📊 DATABASE STRUKTURASI

### users jadvali
```sql
user_id INTEGER PRIMARY KEY
full_name TEXT NOT NULL
username TEXT
registration_date TIMESTAMP
is_active BOOLEAN
```

### test_keys jadvali
```sql
test_id TEXT PRIMARY KEY
correct_answers TEXT NOT NULL
total_questions INTEGER NOT NULL
certificate_template TEXT
created_by_admin INTEGER
created_at TIMESTAMP
```

### test_results jadvali
```sql
id INTEGER PRIMARY KEY
user_id INTEGER
test_id TEXT
correct_answers INTEGER
wrong_answers INTEGER
score_percentage REAL
wrong_questions TEXT
submitted_at TIMESTAMP
certificate_issued BOOLEAN
```

---

## 🔐 XAVFSIZLIK

1. **.env faylini hech qachon Git ga yuklang!**
   - `.gitignore` ga qo'shilgan
   - Token maxfiy saqlanishi kerak

2. **Admin ID larni ehtiyotkorlik bilan qo'shing**
   - Faqat ishonchli odamlar

3. **Database backup oling:**
   ```bash
   cp bot.db backups/bot_$(date +%Y%m%d).db
   ```

---

## 📞 YORDAM

Muammo yuzaga kelsa:

1. **Log faylni tekshiring:** `logs/bot.log`
2. **Konfiguratsiyani tekshiring:** `python3 config.py`
3. **Database backupini oling**
4. **GitHub issues:** (agar ochiq source bo'lsa)

---

## 📝 LICENSE

MIT License - O'z ehtiyojingizga moslang!

---

## 👨‍💻 DEVELOPER

**AI Assistant** tarafidan yaratildi  
Telegram: [Your Contact]  
GitHub: [Your GitHub]

---

## 🎉 BOT TAYYOR!

```bash
# Ishga tushiring
python3 bot.py

# Va marhamat! ✅
```

**Muvaffaqiyatlar! 🚀**
