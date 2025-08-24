#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных на Railway
Запустите этот скрипт после деплоя в Railway Console
"""

import os
from dotenv import load_dotenv
from app import app, db, User
from werkzeug.security import generate_password_hash

def setup_database():
    """Инициализирует базу данных и создает администратора"""
    
    with app.app_context():
        try:
            print("🗄️ Создаем таблицы базы данных...")
            db.create_all()
            print("✅ Таблицы созданы успешно")
            
            # Создаем администратора по умолчанию
            print("👤 Проверяем администратора...")
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@fleet.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Администратор создан: admin/admin123")
            else:
                print("ℹ️ Администратор уже существует")
                
            print("🎉 База данных инициализирована успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    setup_database()
