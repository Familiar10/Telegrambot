import random
import sys
from database import Database

NAMES = ["Ali", "Vali", "G'ani", "Hasan", "Husan", "Sardor", "Rustam", "Jasur", "Umid", "Farruh", 
         "Malika", "Sevara", "Nargiza", "Dilnoza", "Zilola", "Shahnoza", "Madina", "Nodira", "Iroda"]
SURNAMES = ["Karimov", "Abdullayev", "Rustamov", "Toshmatov", "Eshmatov", "Qodirov", "Nazarov", 
            "Murodov", "Jalilov", "Ibragimov", "Yusupov", "Umarov", "Olimov", "Rahimov"]

def generate_fake_name():
    return f"{random.choice(NAMES)} {random.choice(SURNAMES)}"

def main():
    db = Database('bot.db')
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 1. Get latest test ID
    cursor.execute('SELECT test_id, correct_answers, total_questions FROM test_keys ORDER BY created_at DESC LIMIT 1')
    row = cursor.fetchone()
    
    if not row:
        print("Xatolik: Hech qanday test topilmadi. Avval /newtest orqali test yarating.")
        sys.exit(1)
        
    test_id, correct_answers_str, total_questions = row[0], row[1], row[2]
    print(f"Test topildi: {test_id} ({total_questions} ta savol)")
    
    print("100 ta o'quvchi qo'shilmoqda...")
    for i in range(1, 101):
        fake_user_id = 1000000 + i
        fake_name = generate_fake_name()
        
        # Insert User
        cursor.execute("INSERT OR REPLACE INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
                       (fake_user_id, fake_name, f"user{fake_user_id}"))
        
        # Generate random result (mostly good ones if possible, but totally random)
        correct_count = random.randint(max(0, total_questions // 2), total_questions) # Skew towards passing
        wrong_count = total_questions - correct_count
        percentage = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0
        
        # Fake wrong questions
        wrong_q_list = random.sample(range(1, total_questions + 1), wrong_count)
        
        # Check if already submitted
        cursor.execute("SELECT 1 FROM test_results WHERE user_id = ? AND test_id = ?", (fake_user_id, test_id))
        if not cursor.fetchone():
            certificate_issued = percentage >= 70
            cursor.execute('''
                INSERT INTO test_results 
                (user_id, test_id, correct_answers, wrong_answers, score_percentage, wrong_questions, certificate_issued)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fake_user_id, test_id, correct_count, wrong_count, percentage, str(wrong_q_list), certificate_issued))
    
    conn.commit()
    conn.close()
    print("Muvaffaqiyatli yakunlandi! Botda /stat yoki /leaderboard komandalarini tekshirib ko'ring.")

if __name__ == '__main__':
    main()
