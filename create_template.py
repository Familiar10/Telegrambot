#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖼️ Certificate Template Creator
Oddiy sertifikat shablonini yaratish
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_template():
    """Juda oddiy sertifikat shablonini yaratish (orqa fon muammosi bo'lsa)"""
    print("Sertifikat shabloni yaratilmoqda...")
    
    # 1920x1080 o'lchamda oq fon
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Ramka chizish
    border_color = (50, 100, 200)
    border_width = 20
    draw.rectangle(
        [(border_width, border_width), 
         (width - border_width, height - border_width)],
        outline=border_color,
        width=border_width
    )
    
    # Ichki ramka
    inner_border = border_width + 30
    draw.rectangle(
        [(inner_border, inner_border), 
         (width - inner_border, height - inner_border)],
        outline=(100, 150, 220),
        width=5
    )
    
    # Fontlarni yuklash
    try:
        title_font = ImageFont.truetype('fonts/Arial.ttf', 100)
        subtitle_font = ImageFont.truetype('fonts/Arial.ttf', 40)
        text_font = ImageFont.truetype('fonts/Arial.ttf', 30)
    except IOError:
        print("Arial.ttf topilmadi, default font ishlatilmoqda")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        
    # "SERTIFIKAT" yozuvi
    title_text = "SERTIFIKAT"
    
    if title_font != ImageFont.load_default():
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        draw.text(
            (title_x, 150),
            title_text,
            font=title_font,
            fill=(50, 100, 200)
        )
        
        # "Bu sertifikat beriladi:" yozuvi
        subtitle_text = "Bu sertifikat beriladi:"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        
        draw.text(
            (subtitle_x, 300),
            subtitle_text,
            font=subtitle_font,
            fill=(100, 100, 100)
        )
        
        # ISM JOYI (bu yerga dinamik ism qo'yiladi)
        # Chiziq
        line_y = 540
        line_margin = 300
        draw.line(
            [(line_margin, line_y), (width - line_margin, line_y)],
            fill=(150, 150, 150),
            width=3
        )
        
        # "Test muvaffaqiyatli yakunlanganligi uchun" yozuvi
        footer_text = "Test muvaffaqiyatli yakunlanganligi uchun"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=subtitle_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (width - footer_width) // 2
        
        draw.text(
            (footer_x, 650),
            footer_text,
            font=subtitle_font,
            fill=(100, 100, 100)
        )
        
        # Imzo joylari
        signature_y = 850
        
        # Chap imzo
        draw.line(
            [(200, signature_y), (500, signature_y)],
            fill=(150, 150, 150),
            width=2
        )
        draw.text(
            (250, signature_y + 20),
            "Mudir",
            font=text_font,
            fill=(100, 100, 100)
        )
        
        # O'ng imzo
        draw.line(
            [(width - 500, signature_y), (width - 200, signature_y)],
            fill=(150, 150, 150),
            width=2
        )
        draw.text(
            (width - 450, signature_y + 20),
            "O'qituvchi",
            font=text_font,
            fill=(100, 100, 100)
        )
    else:
        # Default font uchun oddiy matn
        draw.text((width // 2 - 100, 150), "SERTIFIKAT", fill=(50, 100, 200))
        draw.text((width // 2 - 150, 300), "Bu sertifikat beriladi:", fill=(100, 100, 100))
        draw.line([(300, 540), (width - 300, 540)], fill=(150, 150, 150), width=3)
        draw.text((width // 2 - 250, 650), "Test muvaffaqiyatli yakunlanganligi uchun", fill=(100, 100, 100))
    
    # Saqlash
    os.makedirs('templates', exist_ok=True)
    output_path = 'templates/certificate_template.png'
    img.save(output_path, quality=95)
    
    print(f"Shablon yaratildi: {output_path}")
    print(f"O'lcham: {width}x{height} px")
    print("\nEndi /newtest komandasi bilan bu shablonni ishlatishingiz mumkin!")
    
    return output_path

if __name__ == '__main__':
    create_simple_template()
