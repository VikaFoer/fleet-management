#!/usr/bin/env python3
"""
Скрипт для настройки PythonAnywhere
Запустите этот скрипт локально, чтобы подготовить файлы для загрузки
"""

import os
import shutil
from pathlib import Path

def create_pythonanywhere_package():
    """Создает пакет файлов для PythonAnywhere"""
    
    print("🚀 Создание пакета для PythonAnywhere")
    print("=" * 50)
    
    # Создаем папку для PythonAnywhere
    pa_folder = Path("pythonanywhere_package")
    if pa_folder.exists():
        shutil.rmtree(pa_folder)
    pa_folder.mkdir()
    
    # Копируем основные файлы
    files_to_copy = [
        "app.py",
        "requirements.txt",
        "config.py",
        "init_db.py",
        ".env",
        "README.md"
    ]
    
    folders_to_copy = [
        "templates"
    ]
    
    print("📁 Копируем файлы...")
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, pa_folder / file_name)
            print(f"✅ {file_name}")
        else:
            print(f"⚠️ {file_name} не найден")
    
    print("📁 Копируем папки...")
    for folder_name in folders_to_copy:
        if Path(folder_name).exists():
            shutil.copytree(folder_name, pa_folder / folder_name)
            print(f"✅ {folder_name}/")
        else:
            print(f"⚠️ {folder_name}/ не найден")
    
    # Создаем инструкции для PythonAnywhere
    instructions = """# 🚀 Инструкции по развертыванию на PythonAnywhere

## Шаг 1: Создайте аккаунт
1. Перейдите на https://www.pythonanywhere.com
2. Создайте бесплатный аккаунт

## Шаг 2: Загрузите файлы
1. В PythonAnywhere перейдите в раздел "Files"
2. Создайте папку `fleet-management`
3. Загрузите все файлы из этой папки в `fleet-management`

## Шаг 3: Создайте Web App
1. Перейдите в раздел "Web"
2. Нажмите "Add a new web app"
3. Выберите "Flask"
4. Выберите Python 3.11
5. Укажите путь: `/home/yourusername/fleet-management/app.py`

## Шаг 4: Настройте WSGI файл
1. Откройте файл `/var/www/yourusername_pythonanywhere_com_wsgi.py`
2. Замените содержимое на:

```python
import sys
path = '/home/yourusername/fleet-management'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

## Шаг 5: Установите зависимости
1. Перейдите в "Consoles" → "Bash"
2. Выполните команды:

```bash
cd fleet-management
pip install -r requirements.txt
```

## Шаг 6: Создайте .env файл
```bash
echo "SECRET_KEY=your-super-secret-key-here" > .env
echo "DATABASE_URL=sqlite:///fleet.db" >> .env
echo "FLASK_ENV=production" >> .env
echo "FLASK_DEBUG=False" >> .env
```

## Шаг 7: Инициализируйте базу данных
```bash
python init_db.py
```

## Шаг 8: Перезапустите Web App
1. Вернитесь в "Web" раздел
2. Нажмите "Reload"

## Логин:
- **Логин:** admin
- **Пароль:** admin123

## URL вашего приложения:
https://yourusername.pythonanywhere.com
"""
    
    with open(pa_folder / "INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    # Создаем ZIP архив
    print("📦 Создаем ZIP архив...")
    shutil.make_archive("fleet-management-pythonanywhere", "zip", pa_folder)
    
    print("\n🎉 Готово!")
    print(f"📁 Папка создана: {pa_folder}")
    print("📦 ZIP архив: fleet-management-pythonanywhere.zip")
    print("\n📋 Следующие шаги:")
    print("1. Загрузите ZIP архив на PythonAnywhere")
    print("2. Следуйте инструкциям в INSTRUCTIONS.md")
    print("3. Или используйте файл pythonanywhere_deploy.md")

if __name__ == '__main__':
    create_pythonanywhere_package()
