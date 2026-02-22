import os
from PIL import Image, ImageDraw, ImageFont

def generate_aesthetic_template():
    """Yangi, chiroyli va rasmiy sertifikat shablonini yaratish."""
    width, height = 1920, 1080
    
    # Orqa fon (Och sarg'ish - rasmiy qog'oz rangi)
    img = Image.new('RGB', (width, height), color=(252, 250, 245))
    draw = ImageDraw.Draw(img)
    
    # Ranglar
    primary_color = (15, 32, 67)      # To'q ko'k
    secondary_color = (212, 175, 55)  # Oltin rang
    gray_color = (80, 80, 80)         # To'q kulrang
    
    # Tashqi qalin ramka (To'q ko'k)
    draw.rectangle([40, 40, width-40, height-40], outline=primary_color, width=20)
    # Ichki ingichka oltin ramka
    draw.rectangle([70, 70, width-70, height-70], outline=secondary_color, width=5)
    
    # Burchaklardagi oltin bezaklar
    d = 100
    draw.polygon([(70, 70), (70+d, 70), (70, 70+d)], fill=secondary_color)
    draw.polygon([(width-70, 70), (width-70-d, 70), (width-70, 70+d)], fill=secondary_color)
    draw.polygon([(70, height-70), (70+d, height-70), (70, height-70-d)], fill=secondary_color)
    draw.polygon([(width-70, height-70), (width-70-d, height-70), (width-70, height-70-d)], fill=secondary_color)

    # Fontlarni yuklash
    try:
        title_font = ImageFont.truetype('fonts/Arial.ttf', 140)
        subtitle_font = ImageFont.truetype('fonts/Arial.ttf', 55)
        text_font = ImageFont.truetype('fonts/Arial.ttf', 45)
        small_font = ImageFont.truetype('fonts/Arial.ttf', 35)
    except IOError:
        print("Font topilmadi, default font ishlatilmoqda")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        
    # Asosiy Sarlavha
    title = "S E R T I F I K A T"
    if title_font != ImageFont.load_default():
        bbox = draw.textbbox((0, 0), title, font=title_font)
        t_w = bbox[2] - bbox[0]
        draw.text(((width - t_w) / 2, 120), title, font=title_font, fill=primary_color)
        
        # Tashkilot yoki kanal nomi
        channel_name = "@TeacherRahmatjon_math"
        bbox_c = draw.textbbox((0, 0), channel_name, font=subtitle_font)
        c_w = bbox_c[2] - bbox_c[0]
        draw.text(((width - c_w) / 2, 260), channel_name, font=subtitle_font, fill=secondary_color)
        
        # O'rta qism yozuvlari
        desc1 = "Ushbu sertifikat"
        bbox_d1 = draw.textbbox((0, 0), desc1, font=text_font)
        d1_w = bbox_d1[2] - bbox_d1[0]
        draw.text(((width - d1_w) / 2, 360), desc1, font=text_font, fill=gray_color)
        
        # Ism qismi uchun chiziq va bo'sh joy
        # DIQQAT: certificate_gen.py ismni aynan (height // 2 - 50) => 490 da yozadi. 
        # Shuning uchun ismning tagiga yoziladigan chiziqni biroz pastga, masalan 560 ga chizamiz
        draw.line([(400, 560), (width - 400, 560)], fill=secondary_color, width=4)
        
        # DIQQAT: certificate_gen.py ball va sanani (height // 2 + 80) => 620 da yozadi.
        # Bu qismi bo'sh bo'lishi kerak.
        
        # Qanday oldi? (Bularni 720 va 780 ga tushiramiz)
        desc2 = "Rahmatjon Boltaboyev tomonidan tashkil etilgan maxsus sinov testida"
        desc3 = "matematika fanidan a'lo natija ko'rsatgani uchun munosib ravishda taqdim etildi."
        
        bbox_d2 = draw.textbbox((0, 0), desc2, font=text_font)
        d2_w = bbox_d2[2] - bbox_d2[0]
        draw.text(((width - d2_w) / 2, 700), desc2, font=text_font, fill=gray_color)
        
        bbox_d3 = draw.textbbox((0, 0), desc3, font=text_font)
        d3_w = bbox_d3[2] - bbox_d3[0]
        draw.text(((width - d3_w) / 2, 760), desc3, font=text_font, fill=gray_color)
        
        # Imzolar joylashuvi (Pastda 950 larda)
        # O'qituvchi va Mudir imzosi
        draw.line([(350, 950), (750, 950)], fill=primary_color, width=3)
        draw.text((550, 970), "Rahmatjon Boltaboyev", font=text_font, fill=primary_color, anchor="mm")
        draw.text((550, 1010), "(O'qituvchi - @TeacherRahmatjon_math)", font=small_font, fill=gray_color, anchor="mm")
        
        draw.line([(width - 750, 950), (width - 350, 950)], fill=primary_color, width=3)
        # Men O'ng tomonga Tasdiqlash belgisini va sana so'zini qoldirdim
        draw.text((width - 550, 970), "Matematika Fani", font=text_font, fill=primary_color, anchor="mm")
        draw.text((width - 550, 1010), "(Guruh Ma'muriyati)", font=small_font, fill=gray_color, anchor="mm")
        
    os.makedirs('templates', exist_ok=True)
    template_path = os.path.join('templates', 'default_template.png')
    img.save(template_path, quality=100)
    print(f"Juda chiroyli shablon yaratildi: {template_path}")

if __name__ == '__main__':
    generate_aesthetic_template()
