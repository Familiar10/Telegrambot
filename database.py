#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Database Management System
Foydalanuvchilar, testlar va natijalarni boshqarish
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Database bilan bog'lanish"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Database jadvallarini yaratish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                username TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Test keys jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_keys (
                test_id TEXT PRIMARY KEY,
                correct_answers TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                certificate_template TEXT,
                created_by_admin INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration TEXT,
                start_time TIMESTAMP,
                duration_minutes INTEGER
            )
        ''')
        
        # Migratsiya: ustunlarni qo'shish
        try:
            cursor.execute('ALTER TABLE test_keys ADD COLUMN start_time TIMESTAMP')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE test_keys ADD COLUMN duration_minutes INTEGER')
        except sqlite3.OperationalError:
            pass

        # Test results jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_id TEXT NOT NULL,
                correct_answers INTEGER NOT NULL,
                wrong_answers INTEGER NOT NULL,
                score_percentage REAL NOT NULL,
                wrong_questions TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                certificate_issued BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (test_id) REFERENCES test_keys (test_id)
            )
        ''')
        
        # Settings table for simulation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== USER FUNKSIYALARI ==========
    
    def user_exists(self, user_id: int) -> bool:
        """Foydalanuvchi mavjudligini tekshirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def add_user(self, user_id: int, full_name: str, username: str = None):
        """Yangi foydalanuvchi qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, full_name, username)
            VALUES (?, ?, ?)
        ''', (user_id, full_name, username))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumotlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'full_name': row[1],
                'username': row[2],
                'registration_date': row[3],
                'is_active': row[4]
            }
        return None
    
    # ========== TEST KEYS FUNKSIYALARI ==========
    
    def add_test_key(self, test_id: str, correct_answers: str, 
                     template_path: str, admin_id: int, duration: str = None,
                     start_time: str = None, duration_minutes: int = 0):
        """Yangi test kalitini qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO test_keys 
            (test_id, correct_answers, total_questions, certificate_template, 
             created_by_admin, duration, start_time, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (test_id, correct_answers, len(correct_answers), template_path, 
              admin_id, duration, start_time, duration_minutes))
        conn.commit()
        conn.close()
    
    def get_test_key(self, test_id: str) -> Optional[Dict]:
        """Test kalitini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM test_keys WHERE test_id = ?', (test_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Ustunlar soniga qarab ma'lumotlarni olish
            duration = row[6] if len(row) > 6 else None
            start_time = row[7] if len(row) > 7 else None
            duration_minutes = row[8] if len(row) > 8 else 0
            
            return {
                'test_id': row[0],
                'correct_answers': row[1],
                'total_questions': row[2],
                'certificate_template': row[3],
                'created_by_admin': row[4],
                'created_at': row[5],
                'duration': duration,
                'start_time': start_time,
                'duration_minutes': duration_minutes
            }
        return None
    
    # ========== TEST RESULTS FUNKSIYALARI ==========
    
    def save_test_result(self, user_id: int, test_id: str, 
                        correct: int, wrong: int, percentage: float,
                        wrong_questions: List[int], certificate_issued: bool = False):
        """Test natijasini saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO test_results 
            (user_id, test_id, correct_answers, wrong_answers, 
             score_percentage, wrong_questions, certificate_issued)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, test_id, correct, wrong, percentage, 
              json.dumps(wrong_questions), certificate_issued))
        conn.commit()
        conn.close()
    
    def has_certificate(self, user_id: int, test_id: str) -> bool:
        """Foydalanuvchi bu testdan sertifikat olganligini tekshirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM test_results 
            WHERE user_id = ? AND test_id = ? AND certificate_issued = TRUE
        ''', (user_id, test_id))
        has_cert = cursor.fetchone() is not None
        conn.close()
        return has_cert

    def check_test_submission(self, user_id: int, test_id: str) -> bool:
        """Foydalanuvchi bu testni yechganligini tekshirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM test_results 
            WHERE user_id = ? AND test_id = ?
        ''', (user_id, test_id))
        submitted = cursor.fetchone() is not None
        conn.close()
        return submitted
    
    def get_user_results(self, user_id: int) -> List[Dict]:
        """Foydalanuvchining barcha natijalarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT test_id, correct_answers, wrong_answers, 
                   score_percentage, submitted_at, certificate_issued, wrong_questions
            FROM test_results
            WHERE user_id = ?
            ORDER BY submitted_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'test_id': row[0],
                'correct': row[1],
                'wrong': row[2],
                'percentage': row[3],
                'date': row[4],
                'certificate': row[5],
                'wrong_questions': row[6]
            })
        return results
        
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Top o'quvchilar ro'yxati (umumiy ball bo'yicha)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Har bir foydalanuvchining to'g'ri javoblari yig'indisini hisoblash
        query = '''
            SELECT u.full_name, SUM(tr.correct_answers) as total_score
            FROM test_results tr
            JOIN users u ON tr.user_id = u.user_id
            GROUP BY tr.user_id
            ORDER BY total_score DESC
            LIMIT ?
        '''
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        leaderboard = []
        for row in rows:
            leaderboard.append({
                'full_name': row[0],
                'total_score': row[1]
            })
        return leaderboard
    
    def get_user_rank(self, user_id: int) -> Dict:
        """Foydalanuvchi reytingini aniqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Barcha foydalanuvchilar ballari
        query = '''
            SELECT user_id, SUM(correct_answers) as total_score
            FROM test_results
            GROUP BY user_id
            ORDER BY total_score DESC
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        rank = 0
        total_score = 0
        
        for i, row in enumerate(rows, 1):
            if row[0] == user_id:
                rank = i
                total_score = row[1]
                break
                
        return {
            'rank': rank,
            'total_score': total_score,
            'total_users': len(rows)
        }

    def delete_test(self, test_id: str) -> bool:
        """Testni o'chirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Avval natijalarni o'chirish
            cursor.execute('DELETE FROM test_results WHERE test_id = ?', (test_id,))
            # Keyin testni o'chirish
            cursor.execute('DELETE FROM test_keys WHERE test_id = ?', (test_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Xatolik: {e}")
            return False
        finally:
            conn.close()

    def get_all_tests(self) -> List[Dict]:
        """Barcha testlar ro'yxatini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT test_id, total_questions, created_at, duration
            FROM test_keys
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        tests = []
        for row in rows:
            tests.append({
                'test_id': row[0],
                'questions': row[1],
                'created_at': row[2],
                'duration': row[3]
            })
        return tests
    
    # ========== STATISTIKA ==========
    
    # ========== SETTINGS FUNKSIYALARI ==========
    
    def set_setting(self, key: str, value: str):
        """Sozlamani saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
        
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Sozlamani olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default

    # ========== STATISTIKA ==========
    
    def get_all_users_count(self) -> int:
        """Barcha foydalanuvchilar soni (simulyatsiya hisobga olingan)"""
        # Avval simulyatsiya qilingan sonni tekshirish
        fake_count = self.get_setting('fake_user_count')
        if fake_count:
            return int(fake_count)
            
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_real_users_count(self) -> int:
        """Haqiqiy foydalanuvchilar soni"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def export_statistics(self) -> str:
        """Statistikani Excel ga eksport qilish"""
        conn = self.get_connection()
        
        query = '''
            SELECT 
                u.full_name as "Ism-Familiya",
                u.username as "Username",
                t.test_id as "Test ID",
                t.correct_answers as "To'g'ri",
                t.wrong_answers as "Xato",
                t.score_percentage as "Ball (%)",
                CASE 
                    WHEN t.certificate_issued = 1 THEN 'Ha'
                    ELSE "Yo'q"
                END as "Sertifikat",
                t.submitted_at as "Sana"
            FROM test_results t
            JOIN users u ON t.user_id = u.user_id
            ORDER BY t.submitted_at DESC
        '''
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Excel ga saqlash
        excel_path = 'statistics.xlsx'
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Natijalar')
            
            # Formatlash
            worksheet = writer.sheets['Natijalar']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return excel_path
    
    def get_statistics_summary(self) -> Dict:
        """Umumiy statistika"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Jami testlar
        cursor.execute('SELECT COUNT(*) FROM test_results')
        total_tests = cursor.fetchone()[0]
        
        # Sertifikat olganlar
        cursor.execute('SELECT COUNT(*) FROM test_results WHERE certificate_issued = TRUE')
        certificates = cursor.fetchone()[0]
        
        # O'rtacha ball
        cursor.execute('SELECT AVG(score_percentage) FROM test_results')
        avg_score = cursor.fetchone()[0] or 0
        
        # Jami foydalanuvchilar
        total_users = self.get_all_users_count()
        
        conn.close()
        
        return {
            'total_tests': total_tests,
            'certificates': certificates,
            'avg_score': round(avg_score, 2),
            'total_users': total_users
        }
