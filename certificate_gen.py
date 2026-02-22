#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 Certificate Generator
Sertifikat yaratish va formatni sozlash
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

class CertificateGenerator:
    
    @staticmethod
    def generate(full_name: str, test_id: str, score: float, 
                 template_path: str, user_id: int) -> str:
        """
        Sertifikat generatsiya qilish
        
        Args:
            full_name: Foydalanuvchi ismi
            test_id: Test IDsi
            score: Ball (%)
            template_path: Shablon fayl yo'li
            user_id: Foydalanuvchi ID
            
        Returns:
            Yaratilgan sertifikat fayl yo'li
        """
        try:
            # Shablonni yuklash
            if not os.path.exists(template_path):
                print(f"Shablon topilmadi: {template_path}")
                return None
                
            img = Image.open(template_path)
            draw = ImageDraw.Draw(img)
            
            # Dinamik font o'lchamlari
            base_size = int(img.width * 0.025)  # Juda ham kichikroq, vizualga mos (Oldin 0.04 edi)
            small_size = int(img.width * 0.02) 
            
            # Agar Arial mavjud bo'lmasa, default fontdan foydalanish
            try:
                # Windows system font or local fonts/Arial.ttf
                try:
                    font_name = ImageFont.truetype("arial.ttf", base_size)
                    font_details = ImageFont.truetype("arial.ttf", small_size)
                except IOError:
                    font_path = os.path.join('fonts', 'Arial.ttf')
                    font_name = ImageFont.truetype(font_path, base_size)
                    font_details = ImageFont.truetype(font_path, small_size)
            except Exception as e:
                print(f"Font yuklanmadi, default ishlatilmoqda: {e}")
                font_name = ImageFont.load_default()
                font_details = ImageFont.load_default()
            
            # Ranglar
            name_color = (255, 150, 180) # Pushti
            details_color = (200, 200, 200) # Och kulrang
            
            # 1. ISM YOZISH
            # "NAME" yozuvi taxminan 65% balandlikda chiziqning ustida. Endi sal chaproqdan (masalan 15% yoki 20% X o'qidan) boshlaymiz.
            start_x = int(img.width * 0.15)
            line_y = int(img.height * 0.65)
            
            if font_name == ImageFont.load_default():
                draw.text((start_x, line_y - 30), full_name, font=font_name, fill=name_color)
                # Kichik hisoblash (default font uchun qiyinroq), text o'lchamini olib davomiga yozamiz
                bbox = draw.textbbox((0, 0), full_name, font=font_name)
                name_width = bbox[2] - bbox[0]
            else:
                draw.text((start_x, line_y), full_name, font=font_name, fill=name_color, anchor="ld") # anchor="ld" - chapki pastki burchak
                name_width = draw.textlength(full_name, font=font_name)
            
            # 2. BALL YOZISH
            # Ism tugagan joydan biroz joy tashlab (masalan 30 piksel) natijani yozamiz
            details = f"|  Natija: {score}%"
            score_x = start_x + name_width + 40
            
            if font_details == ImageFont.load_default():
                draw.text((score_x, line_y - 25), details, font=font_details, fill=details_color)
            else:
                draw.text((score_x, line_y), details, font=font_details, fill=details_color, anchor="ld")
            
            # Certificates papkasini yaratish
            os.makedirs('certificates', exist_ok=True)
            
            # Saqlash (PNG)
            output_filename_png = f"{user_id}_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            output_path_png = os.path.join('certificates', output_filename_png)
            img.save(output_path_png, quality=95)
            
            # Saqlash (PDF)
            output_filename_pdf = f"{user_id}_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path_pdf = os.path.join('certificates', output_filename_pdf)
            
            # PDF uchun RGB ga o'tkazish kerak (agar RGBA bo'lsa)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            img.save(output_path_pdf, "PDF", resolution=100.0)
            
            print(f"Sertifikat yaratildi: {output_filename_pdf}")
            return output_path_pdf
            
        except Exception as e:
            print(f"Sertifikat yaratishda xatolik: {e}")
            import traceback
            traceback.print_exc()
            return None
