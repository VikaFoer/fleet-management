#!/usr/bin/env python3
"""
Упрощенный скрипт для запуска Fleet Management System
"""

import os
import sys
import secrets
from pathlib import Path

def main():
    print("🚀 Fleet Management System - Быстрый запуск")
    print("=" * 50)
    
    # Создаем .env файл если его нет
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Создаем файл .env...")
        secret_key = secrets.token_hex(32)
        env_content = f"""SECRET_KEY={secret_key}
DATABASE_URL=sqlite:///fleet.db
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print(f"✅ Файл .env создан")
    
    # Проверяем виртуальное окружение
    if not Path("venv").exists():
        print("🐍 Создаем виртуальное окружение...")
        os.system("python -m venv venv")
    
    # Устанавливаем основные зависимости
    print("📦 Устанавливаем зависимости...")
    
    # Устанавливаем по одной, чтобы избежать конфликтов
    dependencies = [
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5", 
        "Flask-Login==0.6.3",
        "python-dotenv==1.0.0",
        "Werkzeug==2.3.7",
        "Jinja2==3.1.2"
    ]
    
    for dep in dependencies:
        print(f"📥 Устанавливаем {dep}...")
        os.system(f"venv\\Scripts\\pip install {dep}")
    
    # Инициализируем базу данных
    print("🗄️ Инициализируем базу данных...")
    
    init_script = """
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from app import app, db, User
from werkzeug.security import generate_password_hash

def init_database():
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
    init_database()
"""
    
    with open("temp_init.py", "w", encoding="utf-8") as f:
        f.write(init_script)
    
    os.system("python temp_init.py")
    os.remove("temp_init.py")
    
    print("\n🎉 Все готово! Запускаем приложение...")
    print("\n📋 Информация для входа:")
    print("   🌐 URL: http://localhost:5000")
    print("   👤 Логин: admin")
    print("   🔑 Пароль: admin123")
    print("\n⏹️ Для остановки нажмите Ctrl+C")
    print("\n" + "="*50)
    
    # Запускаем приложение
    os.system("python app.py")

if __name__ == '__main__':
    main()
