#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 Database Backup System
Database dan backup olish va tiklash
"""

import shutil
import os
from datetime import datetime
import glob

class BackupManager:
    
    def __init__(self, db_path='bot.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Yangi backup yaratish"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database fayli topilmadi: {self.db_path}")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.backup_dir}/bot_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_file)
            file_size = os.path.getsize(backup_file) / 1024  # KB
            print(f"✅ Backup yaratildi: {backup_file}")
            print(f"📦 Fayl hajmi: {file_size:.2f} KB")
            return backup_file
        except Exception as e:
            print(f"❌ Backup yaratishda xatolik: {e}")
            return None
    
    def list_backups(self):
        """Barcha backuplarni ko'rsatish"""
        backups = sorted(glob.glob(f"{self.backup_dir}/*.db"), reverse=True)
        
        if not backups:
            print("📭 Hech qanday backup topilmadi")
            return []
        
        print(f"\n📦 Mavjud backuplar ({len(backups)} ta):\n")
        
        for i, backup in enumerate(backups, 1):
            file_size = os.path.getsize(backup) / 1024  # KB
            mod_time = datetime.fromtimestamp(os.path.getmtime(backup))
            
            print(f"{i}. {os.path.basename(backup)}")
            print(f"   📅 Sana: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   💾 Hajm: {file_size:.2f} KB")
            print()
        
        return backups
    
    def restore_backup(self, backup_file):
        """Backupdan tiklash"""
        if not os.path.exists(backup_file):
            print(f"❌ Backup fayli topilmadi: {backup_file}")
            return False
        
        try:
            # Hozirgi databasedan backup olish
            if os.path.exists(self.db_path):
                temp_backup = f"{self.backup_dir}/before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(self.db_path, temp_backup)
                print(f"💾 Hozirgi database saqlandi: {temp_backup}")
            
            # Backupdan tiklash
            shutil.copy2(backup_file, self.db_path)
            print(f"✅ Database tiklandi: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Tiklashda xatolik: {e}")
            return False
    
    def clean_old_backups(self, keep_count=10):
        """Eski backuplarni o'chirish"""
        backups = sorted(glob.glob(f"{self.backup_dir}/*.db"))
        
        if len(backups) <= keep_count:
            print(f"ℹ️  {len(backups)} ta backup mavjud (maksimal: {keep_count})")
            return
        
        to_delete = backups[:-keep_count]
        
        print(f"\n🗑️  {len(to_delete)} ta eski backup o'chirilmoqda...")
        
        for backup in to_delete:
            try:
                os.remove(backup)
                print(f"   ✅ O'chirildi: {os.path.basename(backup)}")
            except Exception as e:
                print(f"   ❌ Xatolik: {e}")
        
        print(f"\n✅ Tozalash tugadi. {keep_count} ta backup qoldi.")

def main():
    """Interactive backup dasturi"""
    backup_mgr = BackupManager()
    
    print("\n" + "="*50)
    print("💾 DATABASE BACKUP MANAGER")
    print("="*50 + "\n")
    
    while True:
        print("1. Yangi backup yaratish")
        print("2. Backuplar ro'yxati")
        print("3. Backupdan tiklash")
        print("4. Eski backuplarni tozalash")
        print("5. Chiqish")
        print()
        
        choice = input("Tanlang (1-5): ").strip()
        
        if choice == '1':
            print()
            backup_mgr.create_backup()
            print()
        
        elif choice == '2':
            print()
            backup_mgr.list_backups()
        
        elif choice == '3':
            backups = backup_mgr.list_backups()
            if backups:
                try:
                    index = int(input("Tiklash uchun raqamni kiriting: ")) - 1
                    if 0 <= index < len(backups):
                        confirm = input(f"⚠️  {os.path.basename(backups[index])} tiklansinmi? (y/n): ")
                        if confirm.lower() == 'y':
                            backup_mgr.restore_backup(backups[index])
                    else:
                        print("❌ Noto'g'ri raqam!")
                except ValueError:
                    print("❌ Faqat raqam kiriting!")
            print()
        
        elif choice == '4':
            try:
                count = int(input("Nechta backup qoldirish kerak (default: 10)?: ") or "10")
                backup_mgr.clean_old_backups(keep_count=count)
            except ValueError:
                print("❌ Faqat raqam kiriting!")
            print()
        
        elif choice == '5':
            print("\n👋 Xayr!\n")
            break
        
        else:
            print("❌ Noto'g'ri tanlov!\n")

if __name__ == '__main__':
    main()
