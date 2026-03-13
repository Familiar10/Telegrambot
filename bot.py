#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Professional Test & Certificate Bot
📝 Test tekshirish va sertifikat beruvchi bot
👨‍💻 Developer: AI Assistant
📅 Date: 2026
"""

import re
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)
from telegram.error import TelegramError

from config import BOT_TOKEN, CHANNEL_USERNAME, ADMIN_IDS
from database import Database
from certificate_gen import CertificateGenerator

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database
db = Database('bot.db')

# Conversation states
# Conversation states
WAITING_NAME, WAITING_TEST_ID, WAITING_ANSWERS, WAITING_DURATION, WAITING_TEMPLATE = range(5)

# ============================================
# YORDAMCHI FUNKSIYALAR
# ============================================

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Foydalanuvchini kanalga obuna bo'lganligini tekshirish
    
    Returns:
        True - obuna bo'lgan
        False - obuna bo'lmagan
    """
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return member.status in ['member', 'administrator', 'creator']
    except TelegramError as e:
        logger.error(f"Obunani tekshirishda xatolik (o'tkazib yuborildi): {e}")
        # Xatolik bo'lsa ham ruxsat berish (fail-open)
        return True

async def subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Obuna majburiy - tekshirish va xabar yuborish
    
    Returns:
        True - obuna bor, davom etish mumkin
        False - obuna yo'q, bloklandi
    """
    user_id = update.effective_user.id
    
    if await check_subscription(user_id, context):
        return True
    
    # Obuna yo'q - ogohlantirish
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "⚠️ <b>Botdan foydalanish uchun kanalga obuna bo'ling!</b>\n\n"
        f"📢 Kanal: {CHANNEL_USERNAME}\n\n"
        "Obuna bo'lgandan keyin '✅ Obunani tekshirish' tugmasini bosing."
    )
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')
    return False

def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS

# ============================================
# ASOSIY KOMANDALAR
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start komandasi
    1. Obunani tekshirish
    2. Foydalanuvchi mavjudligini tekshirish
    3. Agar yangi bo'lsa - ism so'rash
    4. Agar mavjud bo'lsa - xush kelibsiz xabari
    """
    user = update.effective_user
    user_id = user.id
    
    # Obunani tekshirish
    if not await subscription_required(update, context):
        return
    
    # Foydalanuvchi mavjudligini tekshirish
    if db.user_exists(user_id):
        user_data = db.get_user(user_id)
        message = (
            f"👋 Assalomu alaykum, <b>{user_data['full_name']}</b>!\n\n"
            "🎯 Test yechish uchun quyidagi formatda kod yuboring:\n"
            "<code>[TestID]*[javoblar]</code>\n\n"
            "📝 Namuna: <code>505*abcdabcd...</code>\n\n"
            "❓ Yordam kerakmi? /help buyrug'ini yuboring."
        )
        await update.message.reply_text(message, parse_mode='HTML')
    else:
        # Yangi foydalanuvchi - ism so'rash
        message = (
            "👋 Xush kelibsiz!\n\n"
            "📝 Sertifikat olish uchun to'liq <b>ism va familiyangizni</b> kiriting:\n\n"
            "Namuna: <code>Rahmatjon Boltaboyev</code>"
        )
        await update.message.reply_text(message, parse_mode='HTML')
        return WAITING_NAME

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam komandasi"""
    if not await subscription_required(update, context):
        return
    
    message = (
        "📖 <b>BOT YORDAMI</b>\n\n"
        "🔹 <b>Test yechish:</b>\n"
        "Format: <code>[TestID]*[javoblar]</code>\n"
        "Namuna: <code>505*abcdabcdabcd</code>\n\n"
        "🔹 <b>Sertifikat olish:</b>\n"
        "70% yoki undan yuqori ball to'plang\n\n"
        "🔹 <b>Natijalarim:</b>\n"
        "/myresults - O'z natijalaringizni ko'ring\n\n"
        "❓ Savollar bo'lsa admin bilan bog'laning"
    )
    
    if is_admin(update.effective_user.id):
        message += (
            "\n\n👑 <b>ADMIN KOMANDALAR:</b>\n"
            "/newtest - Yangi test qo'shish\n"
            "/stat - Statistika\n"
            "/broadcast - Xabar yuborish"
        )
    
    await update.message.reply_text(message, parse_mode='HTML')

async def myresults_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi natijalarini ko'rsatish"""
    if not await subscription_required(update, context):
        return
    
    user = update.effective_user
    user_id = user.id
    results = db.get_user_results(user_id)
    
    if not results:
        await update.message.reply_text(
            "📊 Sizda hali test natijalari yo'q.\n\n"
            "Test yechish uchun kod yuboring!"
        )
        return
    
    message = f"👤 <b>SIZNING PROFILINGIZ: {user.full_name}</b>\n\n"
    
    # Reytingni aniqlash
    rank_data = db.get_user_rank(user_id)
    if rank_data['rank'] > 0:
        message += f"🏆 Reyting: <b>{rank_data['rank']}-o'rin</b> ({rank_data['total_users']} o'quvchi ichida)\n"
    else:
        message += "🏆 Reyting: <b>Aniqlanmagan</b>\n"
        
    message += (
        f"📝 Jami testlar: <b>{len(results)}</b> ta\n"
        f"✅ To'g'ri javoblar: <b>{rank_data['total_score']}</b> ta\n\n"
        "📊 <b>NATIJALAR TARIXI (So'nggi 10 ta):</b>\n\n"
    )
    
    for i, result in enumerate(results[:10], 1):  # Faqat so'ngi 10 ta
        cert_icon = "🏆" if result['certificate'] else "📝"
        wrong_q_list = []
        if result.get('wrong_questions'):
            try:
                import json
                wrong_q_list = json.loads(result['wrong_questions'])
            except:
                pass
        wrong_q_text = f" | ❌ Savollar: {', '.join(map(str, wrong_q_list))}" if wrong_q_list else ""
        message += (
            f"{cert_icon} <b>Test {result['test_id']}</b>\n"
            f"   ✅ {result['correct']} | ❌ {result['wrong']} | 📈 {result['percentage']}%{wrong_q_text}\n"
            f"   📅 {result['date'][:10]}\n\n"
        )
    
    await update.message.reply_text(message, parse_mode='HTML')

# ============================================
# REGISTRATSIYA (Ism qabul qilish)
# ============================================

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi ismini qabul qilish"""
    user = update.effective_user
    full_name = update.message.text.strip()
    
    # Validatsiya
    if len(full_name) < 3 or len(full_name) > 100:
        await update.message.reply_text(
            "❌ Ism juda qisqa yoki juda uzun!\n\n"
            "Iltimos, to'liq ism va familiyangizni kiriting:"
        )
        return WAITING_NAME
    
    # Databasega saqlash
    db.add_user(user.id, full_name, user.username)
    
    message = (
        f"✅ <b>Ro'yxatdan o'tdingiz, {full_name}!</b>\n\n"
        "🎯 Endi test kodini yuborishingiz mumkin:\n"
        "<code>[TestID]*[javoblar]</code>\n\n"
        "📝 Namuna: <code>505*abcdabcd...</code>"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')
    return ConversationHandler.END

# ============================================
# TEST TEKSHIRISH
# ============================================

def validate_test_format(text: str) -> Optional[tuple]:
    """
    Test formatini tekshirish
    
    Returns:
        (test_id, answers) yoki None
    """
    pattern = r'^(\d{3})\*([a-dA-D]{10,100})$'
    match = re.match(pattern, text.strip())
    
    if match:
        return match.group(1), match.group(2).lower()
    return None

def check_answers(user_answers: str, correct_key: str) -> dict:
    """
    Javoblarni tekshirish
    
    Returns:
        {
            'correct': int,
            'wrong': int,
            'percentage': float,
            'wrong_questions': list
        }
    """
    total = len(correct_key)
    correct = 0
    wrong_questions = []
    
    # Har bir javobni tekshirish
    for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_key), 1):
        if user_ans == correct_ans:
            correct += 1
        else:
            wrong_questions.append(i)
    
    wrong = total - correct
    percentage = round((correct / total) * 100, 2)
    
    return {
        'correct': correct,
        'wrong': wrong,
        'percentage': percentage,
        'wrong_questions': wrong_questions,
        'total': total
    }

async def handle_test_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test yuborilganda ishlov berish"""
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    
    # Obunani tekshirish
    if not await subscription_required(update, context):
        return
    
    # Foydalanuvchi ro'yxatdan o'tganligini tekshirish
    if not db.user_exists(user_id):
        await update.message.reply_text(
            "❌ Avval ro'yxatdan o'ting!\n\n"
            "/start buyrug'ini yuboring."
        )
        return
    
    # Format validatsiyasi
    # Agar xabar raqam bilan boshlanmasa, bu test javobi emas deb hisoblaymiz va indamaymiz
    if not text or not text[0].isdigit():
        return

    validation = validate_test_format(text)
    if not validation:
        # Agar raqam bilan boshlansa lekin format noto'g'ri bo'lsa
        await update.message.reply_text(
            "❌ <b>Noto'g'ri format!</b>\n\n"
            "To'g'ri format: <code>[TestID]*[javoblar]</code>\n"
            "Namuna: <code>505*abcdabcd...</code>\n\n"
            "Javoblar faqat a, b, c, d harflaridan iborat bo'lishi kerak.",
            parse_mode='HTML'
        )
        return
    
    test_id, user_answers = validation
    
    # Test kalitini olish
    test_key = db.get_test_key(test_id)
    if not test_key:
        await update.message.reply_text(
            f"❌ <b>Test {test_id} topilmadi!</b>\n\n"
            "Iltimos, to'g'ri Test ID ni kiriting.",
            parse_mode='HTML'
        )
        return

    # Oldin topshirganligini tekshirish
    if db.check_test_submission(user_id, test_id):
        await update.message.reply_text(
            f"⚠️ <b>Siz bu testni (ID: {test_id}) allaqachon yechgansiz!</b>\n\n"
            "Har bir testga faqat bir marta javob yuborish mumkin.",
            parse_mode='HTML'
        )
        return
        
    # Vaqtni tekshirish
    current_time = datetime.now()
    start_time = None
    
    if test_key.get('start_time'):
        start_time_raw = test_key['start_time']
        if isinstance(start_time_raw, datetime):
            start_time = start_time_raw
        elif isinstance(start_time_raw, str):
            # Bir nechta formatni urinib ko'rish
            formats_to_try = [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
            ]
            for fmt in formats_to_try:
                try:
                    start_time = datetime.strptime(start_time_raw, fmt)
                    break
                except ValueError:
                    continue
            
            if start_time is None:
                logger.error(f"start_time formatini parse qilib bo'lmadi: {start_time_raw}")
                # Parse bo'lmasa davom ettiramiz (xatosiz o'tkazib yuboramiz)
    
    # Agar start_time o'rnatilmagan bo'lsa, created_at ni start_time deb faraz qilamiz
    if start_time is None and test_key.get('created_at'):
        created_at_raw = test_key['created_at']
        if isinstance(created_at_raw, datetime):
            start_time = created_at_raw
        elif isinstance(created_at_raw, str):
            try:
                # Odatda SQLite CURRENT_TIMESTAMP "YYYY-MM-DD HH:MM:SS" shaklida bo'ladi
                start_time = datetime.strptime(created_at_raw.split('.')[0], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

    if start_time is not None:
        if test_key.get('start_time') and current_time < start_time:
            await update.message.reply_text(
                f"❌ <b>Test hali boshlanmadi!</b>\n\n"
                f"🕒 Boshlanish vaqti: {start_time.strftime('%Y-%m-%d %H:%M')}",
                parse_mode='HTML'
            )
            return

        duration_mins = test_key.get('duration_minutes', 0)
        
        # Agar duration_minutes 0 bo'lsa, lekin duration matnli bo'lsa (eski testlar uchun fallback)
        if not duration_mins and test_key.get('duration'):
            duration_text = str(test_key.get('duration')).lower()
            match = re.search(r'(\d+)', duration_text)
            if match:
                num = int(match.group(1))
                if 'soat' in duration_text:
                    duration_mins = num * 60
                elif 'kun' in duration_text:
                    duration_mins = num * 24 * 60
                else:
                    duration_mins = num
                    
        if duration_mins and int(duration_mins) > 0:
            end_time = start_time + timedelta(minutes=int(duration_mins))
            if current_time > end_time:
                await update.message.reply_text(
                    f"❌ <b>Test vaqti tugadi!</b>\n\n"
                    f"🏁 Tugash vaqti: {end_time.strftime('%Y-%m-%d %H:%M')}\n"
                    "Afsuski, javoblar qabul qilinmaydi.",
                    parse_mode='HTML'
                )
                return
    
    # Javoblar uzunligini tekshirish
    if len(user_answers) != test_key['total_questions']:
        await update.message.reply_text(
            f"❌ <b>Xato!</b>\n\n"
            f"Bu testda {test_key['total_questions']} ta savol bor.\n"
            f"Siz {len(user_answers)} ta javob yubordingiz.",
            parse_mode='HTML'
        )
        return
    
    # Javoblarni tekshirish
    await update.message.reply_text("⏳ Tekshirilmoqda...")
    
    result = check_answers(user_answers, test_key['correct_answers'])
    
    # Natijani databasega saqlash
    already_has = db.has_certificate(user_id, test_id)
    certificate_issued = result['percentage'] >= 70 and not already_has
    
    db.save_test_result(
        user_id=user_id,
        test_id=test_id,
        correct=result['correct'],
        wrong=result['wrong'],
        percentage=result['percentage'],
        wrong_questions=result['wrong_questions'],
        certificate_issued=certificate_issued
    )
    
    # Natija xabari
    wrong_nums = ', '.join(map(str, result['wrong_questions'])) if result['wrong_questions'] else "Yo'q"
    
    message = (
        "📊 <b>TEST NATIJALARI</b>\n\n"
        f"📝 Test ID: <b>{test_id}</b>\n"
        f"✅ To'g'ri javoblar: <b>{result['correct']}/{result['total']}</b>\n"
        f"❌ Xato javoblar: <b>{result['wrong']}</b>\n"
        f"📈 Ball: <b>{result['percentage']}%</b>\n\n"
        f"❌ Xato savollar: <code>{wrong_nums}</code>\n\n"
    )
    
    # Sertifikat berish (70% dan yuqori)
    if result['percentage'] >= 70:
        # Avval sertifikat olganligini tekshirish
        if already_has:
            message += "ℹ️ <i>Siz bu testdan allaqachon sertifikat oldingiz.</i>"
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            message += "🎉 <b>TABRIKLAYMAN! SERTIFIKAT OLISH HUQUQIGA EGASIZ!</b>\n\n⏳ Sertifikat tayyorlanmoqda..."
            await update.message.reply_text(message, parse_mode='HTML')
            
            # Sertifikat generatsiya qilish
            user_data = db.get_user(user_id)
            cert_path = CertificateGenerator.generate(
                full_name=user_data['full_name'],
                test_id=test_id,
                score=result['percentage'],
                template_path=test_key['certificate_template'],
                user_id=user_id
            )
            
            if cert_path and os.path.exists(cert_path):
                # Sertifikatni yuborish
                with open(cert_path, 'rb') as cert_file:
                    await update.message.reply_document(
                        document=cert_file,
                        filename=os.path.basename(cert_path),
                        caption=(
                            f"🏆 <b>SERTIFIKAT</b>\n\n"
                            f"👤 {user_data['full_name']}\n"
                            f"📝 Test: {test_id}\n"
                            f"📈 Ball: {result['percentage']}%"
                        ),
                        parse_mode='HTML'
                    )
            else:
                await update.message.reply_text(
                    "❌ Sertifikat yaratishda xatolik yuz berdi!\n"
                    "Admin bilan bog'laning."
                )
    else:
        message += "😔 <i>Minimal chegara 70%. Qaytadan urinib ko'ring!</i>"
        await update.message.reply_text(message, parse_mode='HTML')

# ============================================
# ADMIN: YANGI TEST QO'SHISH
# ============================================

async def newtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Yangi test qo'shish jarayonini boshlash"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu komanda faqat adminlar uchun!")
        return
    
    message = (
        "👑 <b>YANGI TEST QO'SHISH</b>\n\n"
        "📝 Test ID kiriting (3 xonali raqam):\n"
        "Namuna: <code>505</code>"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')
    return WAITING_TEST_ID

async def receive_test_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test ID qabul qilish"""
    test_id = update.message.text.strip()
    
    # Validatsiya
    if not re.match(r'^\d{3}$', test_id):
        await update.message.reply_text(
            "❌ Test ID 3 xonali raqam bo'lishi kerak!\n\n"
            "Namuna: <code>505</code>",
            parse_mode='HTML'
        )
        return WAITING_TEST_ID
    
    # Context ga saqlash
    context.user_data['test_id'] = test_id
    
    await update.message.reply_text(
        "✅ Test ID qabul qilindi!\n\n"
        "📝 Endi to'g'ri javoblar kalitini yuboring:\n"
        "Namuna: <code>aabcdcbadcbaabc...</code>\n\n"
        "Faqat a, b, c, d harflaridan foydalaning!"
    )
    return WAITING_ANSWERS

async def receive_test_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test javoblari kalitini qabul qilish"""
    answers = update.message.text.strip().lower()
    
    # Validatsiya
    if not re.match(r'^[a-d]{10,100}$', answers):
        await update.message.reply_text(
            "❌ Javoblar faqat a, b, c, d harflaridan iborat bo'lishi kerak!\n"
            "Kamida 10 ta, ko'pi bilan 100 ta javob bo'lishi mumkin.\n\n"
            "Qaytadan yuboring:"
        )
        return WAITING_ANSWERS
    
    # Context ga saqlash
    context.user_data['answers'] = answers
    
    await update.message.reply_text(
        f"✅ {len(answers)} ta savol qabul qilindi!\n\n"
        "⏳ <b>Test davomiyligi (yoki muddati)ni kiriting:</b>\n"
        "Namuna: <code>2 soat</code> yoki <code>15-martgacha</code>"
    )
    return WAITING_DURATION

async def receive_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test vaqtini qabul qilish va shablonni avtomatik biriktirish"""
    text = update.message.text.strip()
    
    # Format: "2023-10-25 14:00 | 90" (Start time | Duration in minutes)
    # Yoki shunchaki "90" (Hozirdan boshlab 90 minut)
    
    start_time = None
    duration_minutes = 0
    duration_text = text
    
    try:
        if '|' in text:
            parts = text.split('|')
            start_str = parts[0].strip()
            minutes_str = parts[1].strip()
            
            if start_str.lower() == 'hozir':
                start_time = datetime.now()
            else:
                try:
                    start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    await update.message.reply_text(
                        "❌ Sana formati noto'g'ri!\n"
                        "To'g'ri format: YYYY-MM-DD HH:MM (Masalan: 2026-03-15 14:30)\n"
                        "Yoki 'hozir' deb yozing."
                    )
                    return WAITING_DURATION
            
            if minutes_str.isdigit():
                duration_minutes = int(minutes_str)
            else:
                 await update.message.reply_text("❌ Daqiqa faqat raqam bo'lishi kerak!")
                 return WAITING_DURATION
                 
        elif text.isdigit():
            start_time = datetime.now()
            duration_minutes = int(text)
            duration_text = f"{text} daqiqa"
        else:
            # Matnli duration (eski format - son ham qidirish)
            match = re.search(r'(\d+)', text)
            if match:
                num = int(match.group(1))
                if 'soat' in text:
                    duration_minutes = num * 60
                elif 'kun' in text:
                    duration_minutes = num * 24 * 60
                else:
                    duration_minutes = num
                start_time = datetime.now()
            
            duration_text = text
            
    except Exception as e:
        logger.error(f"Vaqtni o'qishda xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos qaytadan kiriting.")
        return WAITING_DURATION

    context.user_data['duration'] = duration_text
    context.user_data['start_time'] = start_time
    context.user_data['duration_minutes'] = duration_minutes
    
    # Avtomatik shablon
    test_id = context.user_data['test_id']
    template_path = os.path.join('templates', 'default_template.png')
    
    # Databasega saqlash
    db.add_test_key(
        test_id=test_id,
        correct_answers=context.user_data['answers'],
        template_path=template_path,
        admin_id=update.effective_user.id,
        duration=context.user_data.get('duration'),
        start_time=context.user_data.get('start_time'),
        duration_minutes=context.user_data.get('duration_minutes', 0)
    )
    
    # Tasdiqlash xabari
    duration_text = f"\n⏳ Vaqt: {context.user_data.get('duration')}" if context.user_data.get('duration') else ""
    message = (
        "✅ <b>TEST MUVAFFAQIYATLI QO'SHILDI!</b>\n\n"
        f"📝 Test ID: <code>{test_id}</code>\n"
        f"📊 Savollar soni: <b>{len(context.user_data['answers'])}</b>"
        f"{duration_text}\n"
        f"🖼 Shablon: Avtomatik sozlangan\n\n"
        "O'quvchilar endi bu testni yecha olishadi!"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')
    
    # Context tozalash
    context.user_data.clear()
    
    return ConversationHandler.END

# ============================================
# ADMIN: STATISTIKA
# ============================================

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Statistikani ko'rish va Excel yuklash"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.effective_message.reply_text("❌ Bu komanda faqat adminlar uchun!")
        return
    
    msg = None
    if not update.callback_query:
        msg = await update.effective_message.reply_text("⏳ Statistika tayyorlanmoqda...")
    
    # Umumiy statistika
    stats = db.get_statistics_summary()
    
    summary_message = (
        "📊 <b>UMUMIY STATISTIKA</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📝 Jami test topshirildi: <b>{stats['total_tests']}</b>\n"
        f"🏆 Sertifikat olganlar: <b>{stats['certificates']}</b>\n"
        f"📈 O'rtacha ball: <b>{stats['avg_score']}%</b>\n\n"
        "📥 Batafsil ma'lumot Excel faylda yuborilmoqda..."
    )
    
    await update.effective_message.reply_text(summary_message, parse_mode='HTML')
    
    # Excel faylni yaratish va yuborish
    try:
        excel_path = db.export_statistics()
        
        with open(excel_path, 'rb') as excel_file:
            await update.effective_message.reply_document(
                document=excel_file,
                filename='statistics.xlsx',
                caption="📊 To'liq statistika Excel formatida"
            )
        
        # Faylni o'chirish
        if os.path.exists(excel_path):
            os.remove(excel_path)
            
        if msg:
            await msg.delete()
        
    except Exception as e:
        logger.error(f"Statistika yuborishda xatolik: {e}")
        await update.effective_message.reply_text(
            "❌ Excel faylni yaratishda xatolik yuz berdi!"
        )

# ============================================
# ADMIN: BROADCAST (Xabar yuborish)
# ============================================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Barcha foydalanuvchilarga xabar yuborish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.effective_message.reply_text("❌ Bu komanda faqat adminlar uchun!")
        return
    
    message = (
        "📢 <b>XABAR YUBORISH</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:\n\n"
        "Bekor qilish: /cancel"
    )
    
    await update.effective_message.reply_text(message, parse_mode='HTML')
    context.user_data['waiting_broadcast'] = True

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast xabarini qabul qilish va yuborish"""
    
    if not context.user_data.get('waiting_broadcast'):
        return
    
    broadcast_text = update.message.text
    
    # Tasdiqlash
    keyboard = [
        [
            InlineKeyboardButton("✅ Ha, yuborish", callback_data="confirm_broadcast"),
            InlineKeyboardButton("❌ Yo'q, bekor qilish", callback_data="cancel_broadcast")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['broadcast_message'] = broadcast_text
    
    preview = broadcast_text[:200] + "..." if len(broadcast_text) > 200 else broadcast_text
    
    await update.effective_message.reply_text(
        f"📢 <b>Xabar ko'rinishi:</b>\n\n{preview}\n\n"
        f"👥 {db.get_all_users_count()} ta foydalanuvchiga yuboriladi.\n\n"
        "Tasdiqlaysizmi?",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def confirm_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast tasdiqlash"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_broadcast":
        await query.edit_message_text("❌ Xabar yuborish bekor qilindi.")
        context.user_data.clear()
        return
    
    # Xabarni yuborish
    broadcast_message = context.user_data.get('broadcast_message')
    
    await query.edit_message_text("⏳ Xabar yuborilmoqda...")
    
    # Barcha foydalanuvchilarni olish
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_active = TRUE")
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    failed_count = 0
    
    for (user_id,) in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>ADMIN XABARI:</b>\n\n{broadcast_message}",
                parse_mode='HTML'
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik: {e}")
            failed_count += 1
    
    result_message = (
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"Muvaffaqiyatli: {success_count}\n"
        f"Xatolik: {failed_count}"
    )
    
    await query.message.reply_text(result_message, parse_mode='HTML')
    context.user_data.clear()

# ============================================
# ADMIN: O'QUVCHI SONINI SOZLASH
# ============================================

async def setusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: O'quvchi sonini sun'iy o'zgartirish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.effective_message.reply_text("❌ Bu komanda faqat adminlar uchun!")
        return
    
    # Argumentlarni tekshirish
    if not getattr(context, 'args', None) and not update.callback_query:
        current_fake = db.get_setting('fake_user_count')
        real_count = db.get_real_users_count()
        
        message = (
            "👥 <b>Foydalanuvchilar sonini sozlash</b>\n\n"
            f"Haqiqiy soni: <b>{real_count}</b>\n"
            f"Hozirgi ko'rsatilayotgan son: <b>{current_fake if current_fake else 'Sozlanmagan (Haqiqiy)'}</b>\n\n"
            "O'zgartirish uchun:\n"
            "<code>/setusers [son]</code> - yangi son o'rnatish\n"
            "<code>/setusers off</code> - o'chirish (haqiqiy sonni ko'rsatish)"
        )
        await update.effective_message.reply_text(message, parse_mode='HTML')
        return
    elif update.callback_query:
        current_fake = db.get_setting('fake_user_count')
        real_count = db.get_real_users_count()
        
        message = (
            "👥 <b>Foydalanuvchilar sonini sozlash</b>\n\n"
            f"Haqiqiy soni: <b>{real_count}</b>\n"
            f"Hozirgi ko'rsatilayotgan son: <b>{current_fake if current_fake else 'Sozlanmagan (Haqiqiy)'}</b>\n\n"
            "Qo'shimcha sozlash uchun yozing:\n"
            "<code>/setusers [son]</code> - yangi son o'rnatish\n"
            "<code>/setusers off</code> - o'chirish (haqiqiy sonni ko'rsatish)"
        )
        await update.effective_message.reply_text(message, parse_mode='HTML')
        return

    arg = context.args[0]
    
    if arg.lower() == 'off':
        db.set_setting('fake_user_count', '')
        await update.effective_message.reply_text("✅ Sun'iy son o'chirildi. Endi haqiqiy son ko'rsatiladi.")
    elif arg.isdigit():
        db.set_setting('fake_user_count', arg)
        await update.effective_message.reply_text(f"✅ Foydalanuvchilar soni <b>{arg}</b> ga o'zgartirildi.", parse_mode='HTML')
    else:
        await update.effective_message.reply_text("❌ Noto'g'ri qiymat! Son kiriting yoki 'off' deb yozing.")

# ============================================
# ADMIN: YANGI PANEL (UI)
# ============================================

async def admin_tests_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Testlar ro'yxati"""
    try:
        query = getattr(update, 'callback_query', None)
        message_to_reply = update.effective_message
        
        tests = db.get_all_tests()
        
        if not tests:
            await message_to_reply.reply_text("📂 Hozircha hech qanday test yo'q.")
            return

        message = "📂 <b>MAVJUD TESTLAR</b>\n\n"
        keyboard = []
        
        for test in tests:
            test_id = test['test_id']
            created = test['created_at'][:10]
            questions = test['questions']
            
            button_text = f"ID: {test_id} | {questions} ta savol | {created}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"admin_test_view_{test_id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Eski xabarni o'chirishga harakat qilamiz
        if query:
            try:
                await query.message.delete()
            except:
                pass
            
        await message_to_reply.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Testlar ro'yxatida xatolik: {e}")
        try:
             await update.effective_message.reply_text("❌ Xatolik yuz berdi!")
        except:
             pass

async def admin_test_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test ma'lumotlarini ko'rish va o'chirish"""
    query = update.callback_query
    test_id = query.data.split('_')[-1]
    
    test = db.get_test_key(test_id)
    
    if not test:
        await query.answer("❌ Test topilmadi!", show_alert=True)
        return

    message = (
        f"📝 <b>TEST MA'LUMOTLARI</b>\n\n"
        f"🆔 ID: <b>{test['test_id']}</b>\n"
        f"❓ Savollar: <b>{test['total_questions']}</b> ta\n"
        f"📅 Yaratilgan: <b>{test['created_at']}</b>\n"
        f"⏱ Vaqt: <b>{test['duration'] or 'Cheklovsiz'}</b>\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🗑 O'chirish", callback_data=f"admin_test_delete_confirm_{test_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_tests_list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.message.delete()
    except:
        pass
        
    await update.effective_message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def admin_test_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'chirishni tasdiqlash"""
    query = update.callback_query
    test_id = query.data.split('_')[-1]
    
    keyboard = [
        [InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"admin_test_delete_{test_id}")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data=f"admin_test_view_{test_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚠️ <b>DIQQAT!</b>\n\n"
        f"Siz rostdan ham <b>Test {test_id}</b> ni o'chirmoqchimisiz?\n"
        "Bu amalni ortga qaytarib bo'lmaydi va barcha natijalar o'chib ketadi!",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def admin_test_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Testni o'chirish"""
    query = update.callback_query
    test_id = query.data.split('_')[-1]
    
    if db.delete_test(test_id):
        await query.answer(f"✅ Test {test_id} o'chirildi!", show_alert=True)
        await admin_tests_list(update, context)
    else:
        await query.answer("❌ Xatolik yuz berdi!", show_alert=True)

async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panelni ochish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.effective_message.reply_text("❌ Bu komanda faqat adminlar uchun!")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Yangi Test", callback_data="admin_new_test"),
         InlineKeyboardButton("📁 Testlar", callback_data="admin_tests_list")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stat"),
         InlineKeyboardButton("👥 O'quvchi Soni", callback_data="admin_setusers")],
        [InlineKeyboardButton("📢 Xabar Yuborish", callback_data="admin_broadcast"),
         InlineKeyboardButton("❌ Yopish", callback_data="admin_close")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.effective_message.reply_text(
        "🛠 <b>ADMIN PANEL</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel tugmalari uchun handler"""
    query = update.callback_query
    
    # Agar conversation handler tomonidan ushlangan bo'lsa, bu yerga kelmasligi kerak
    # Lekin baribir tekshiramiz
    if query.data == "admin_new_test":
        await query.answer()
        
        # We must trigger the entry point manually if falling through, 
        # but PTB ConversationHandler with callbacks might be catching it 
        # so this fallback might just prompt the user directly:
        await query.message.reply_text(
            "👑 <b>YANGI TEST QO'SHISH</b>\n\n"
            "📝 Test ID kiriting (3 xonali raqam):\n"
            "Namuna: <code>505</code>",
            parse_mode='HTML'
        )
        return WAITING_TEST_ID
        
    await query.answer()
    
    data = query.data
    
    if data == "admin_close":
        await query.delete_message()
        return

    elif data == "admin_stat":
        await stat_command(update, context)
        
    elif data == "admin_broadcast":
        await broadcast_command(update, context)
        
    elif data == "admin_setusers":
        await setusers_command(update, context)
        
    elif data == "admin_tests_list":
        await admin_tests_list(update, context)
        
    elif data == "admin_back":
        if update.callback_query:
            try:
                await update.callback_query.message.delete()
            except:
                pass
        await admin_panel_command(update, context)
        
    elif data.startswith("admin_test_view_"):
        await admin_test_view(update, context)
        
    elif data.startswith("admin_test_delete_confirm_"):
        await admin_test_delete_confirm(update, context)
        
    elif data.startswith("admin_test_delete_"):
        await admin_test_delete(update, context)

# ============================================
# LEADERBOARD (REYTING)
# ============================================

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Eng yaxshi o'quvchilar ro'yxati"""
    if not await subscription_required(update, context):
        return

    top_users = db.get_leaderboard()
    
    if not top_users:
        await update.message.reply_text("📊 Hozircha reyting yo'q.")
        return
        
    message = "🏆 <b>TOP 10 O'QUVCHILAR</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, user in enumerate(top_users, 1):
        icon = medals[i-1] if i <= 3 else "👤"
        score = user['total_score']
        name = user['full_name']
        # Ismni qisqartirish agar juda uzun bo'lsa
        if len(name) > 20:
            name = name[:17] + "..."
            
        message += f"{icon} {i}. <b>{name}</b> — {score} ball\n"
        
    await update.message.reply_text(message, parse_mode='HTML')

# ============================================
# CALLBACK QUERY HANDLERS
# ============================================

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
# ... (rest of the file)
    """Obunani tekshirish tugmasi bosilganda"""
    query = update.callback_query
    
    # Har doim answer() chaqirilishini ta'minlash
    try:
        await query.answer()
    except Exception as e:
        logger.error(f"Callback answer xatolik: {e}")
    
    user_id = query.from_user.id
    
    if await check_subscription(user_id, context):
        # Obuna bor
        if db.user_exists(user_id):
            user_data = db.get_user(user_id)
            message = (
                f"✅ Obuna tasdiqlandi!\n\n"
                f"👋 Xush kelibsiz, <b>{user_data['full_name']}</b>!\n\n"
                "🎯 Test kodini yuboring:"
            )
        else:
            message = (
                "✅ Obuna tasdiqlandi!\n\n"
                "📝 Iltimos, ism va familiyangizni kiriting:\n"
                "Namuna: <code>Rahmatjon Ergashev</code>"
            )
        
        await query.edit_message_text(message, parse_mode='HTML')
    else:
        # Hali obuna yo'q
        await query.answer(
            "❌ Siz hali kanalga obuna bo'lmadingiz!",
            show_alert=True
        )

# ============================================
# XATO VA BEKOR QILISH
# ============================================

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har qanday jarayonni bekor qilish"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Jarayon bekor qilindi.\n\n"
        "Boshqa buyruq uchun /help yuboring."
    )
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xatolarni qayd qilish"""
    logger.error(f"Update {update} xatolikka sabab bo'ldi: {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Xatolik yuz berdi! Iltimos, qaytadan urinib ko'ring.\n\n"
                "Muammo davom etsa, admin bilan bog'laning."
            )
        except Exception as e:
            logger.error(f"Xatolik xabarini yuborishda muammo: {e}")

# ============================================
# ASOSIY FUNKSIYA
# ============================================

def main():
    """Botni ishga tushirish"""
    
    # Papkalarni yaratish
    for directory in ['certificates', 'templates', 'fonts', 'logs']:
        os.makedirs(directory, exist_ok=True)
    
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ========== CONVERSATION HANDLERS ==========
    
    # Yangi test qo'shish (Admin)
    newtest_handler = ConversationHandler(
        entry_points=[CommandHandler('newtest', newtest_command), 
                      CallbackQueryHandler(admin_callback, pattern='^admin_new_test$')],
        states={
            WAITING_TEST_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_test_id)],
            WAITING_ANSWERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_test_answers)],
            WAITING_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_duration)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        per_message=False
    )
    
    # Registratsiya
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )
    
    # ========== COMMAND HANDLERS ==========
    
    application.add_handler(registration_handler)
    application.add_handler(newtest_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('myresults', myresults_command))
    application.add_handler(CommandHandler('stat', stat_command))
    application.add_handler(CommandHandler('broadcast', broadcast_command))
    application.add_handler(CommandHandler('setusers', setusers_command))
    application.add_handler(CommandHandler('admin', admin_panel_command))
    application.add_handler(CommandHandler('leaderboard', leaderboard_command))
    application.add_handler(CommandHandler('cancel', cancel_command))
    
    # ========== CALLBACK HANDLERS ==========
    
    application.add_handler(CallbackQueryHandler(
        check_subscription_callback,
        pattern='^check_subscription$'
    ))
    application.add_handler(CallbackQueryHandler(
        confirm_broadcast_callback,
        pattern='^(confirm_broadcast|cancel_broadcast)$'
    ))
    
    # Admin callback handler (ConversationHandler lardan keyin bo'lishi kerak)
    application.add_handler(CallbackQueryHandler(
        admin_callback,
        pattern='^admin_'
    ))
    
    # ========== MESSAGE HANDLERS ==========
    
    async def combined_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.effective_user:
            return
            
        text = update.message.text
        if not text:
            return
            
        # Klaviaturadagi tugmalar uchun tekshiruv (Ekskluziv emoji xatoliklarini oldini olish uchun "in text" ishlash)
        if "Admin Panel" in text:
            await admin_panel_command(update, context)
            return
        elif "Natijalarim" in text:
            await myresults_command(update, context)
            return
        elif "Yordam" in text:
            await help_command(update, context)
            return
        elif "Test topshirish" in text:
            await update.message.reply_text(
                "🎯 <b>Test kodini va javoblarni yuboring!</b>\n\n"
                "To'g'ri format: <code>[TestID]*[javoblar]</code>\n"
                "Namuna: <code>505*abcdabcd...</code>\n\n"
                "<i>Javoblar faqat a, b, c, d harflaridan iborat bo'lishi kerak.</i>",
                parse_mode='HTML'
            )
            return
            
        if context.user_data and context.user_data.get('waiting_broadcast'):
            await handle_broadcast_message(update, context)
        else:
            await handle_test_submission(update, context)

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        combined_text_handler
    ))
    
    # ========== ERROR HANDLER ==========
    
    application.add_error_handler(error_handler)
    
    # ========== BOTNI ISHGA TUSHIRISH ==========
    
    logger.info("Bot ishga tushmoqda...")
    logger.info(f"Kanal: {CHANNEL_USERNAME}")
    logger.info(f"Adminlar: {len(ADMIN_IDS)} ta")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
 
 