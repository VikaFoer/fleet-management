#!/usr/bin/env python3
"""
Автоматический скрипт для запуска Fleet Management System локально
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_step(step, message):
    print(f"\n{'='*50}")
    print(f"🔧 Шаг {step}: {message}")
    print(f"{'='*50}")

def run_command(command, description):
    print(f"\n📋 {description}")
    print(f"💻 Команда: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Успешно: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e.stderr}")
        return False

def main():
    print("🚀 Fleet Management System - Автоматический запуск")
    print("=" * 60)
    
    # Шаг 1: Проверяем Python
    print_step(1, "Проверяем Python")
    if not run_command("python --version", "Проверка версии Python"):
        print("❌ Python не найден. Установите Python 3.8+")
        return False
    
    # Шаг 2: Создаем .env файл если его нет
    print_step(2, "Настройка переменных окружения")
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
        print(f"✅ Файл .env создан с SECRET_KEY: {secret_key[:16]}...")
    else:
        print("ℹ️ Файл .env уже существует")
    
    # Шаг 3: Создаем виртуальное окружение
    print_step(3, "Настройка виртуального окружения")
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🐍 Создаем виртуальное окружение...")
        if not run_command("python -m venv venv", "Создание виртуального окружения"):
            return False
    else:
        print("ℹ️ Виртуальное окружение уже существует")
    
    # Шаг 4: Активируем виртуальное окружение и устанавливаем зависимости
    print_step(4, "Установка зависимостей")
    
    # Определяем команду активации для Windows
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Устанавливаем зависимости
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Установка зависимостей"):
        return False
    
    # Шаг 5: Инициализируем базу данных
    print_step(5, "Инициализация базы данных")
    
    # Создаем скрипт для инициализации БД
    init_script = """
import os
import sys
sys.path.append(os.getcwd())

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
    
    if not run_command(f"{pip_cmd} install python-dotenv", "Установка python-dotenv"):
        return False
    
    if not run_command(f"python temp_init.py", "Инициализация базы данных"):
        return False
    
    # Удаляем временный файл
    os.remove("temp_init.py")
    
    # Шаг 6: Запускаем приложение
    print_step(6, "Запуск приложения")
    print("\n🎉 Все готово! Запускаем приложение...")
    print("\n📋 Информация для входа:")
    print("   🌐 URL: http://localhost:5000")
    print("   👤 Логин: admin")
    print("   🔑 Пароль: admin123")
    print("\n⏹️ Для остановки нажмите Ctrl+C")
    print("\n" + "="*60)
    
    # Запускаем приложение
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(f"{pip_cmd} install python-dotenv && python app.py", shell=True)
        else:  # Linux/Mac
            subprocess.run(f"{pip_cmd} install python-dotenv && python app.py", shell=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Приложение остановлено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
