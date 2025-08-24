#!/bin/bash

echo "🚀 Fleet Management System - Deploy Script"
echo "=========================================="

# Проверяем, что мы в правильной директории
if [ ! -f "app.py" ]; then
    echo "❌ Ошибка: app.py не найден. Убедитесь, что вы в директории fleet-management"
    exit 1
fi

# Генерируем SECRET_KEY если его нет
if [ ! -f ".env" ]; then
    echo "📝 Создаем файл .env..."
    python3 -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" > .env
    echo "DATABASE_URL=sqlite:///fleet.db" >> .env
    echo "FLASK_ENV=production" >> .env
    echo "FLASK_DEBUG=False" >> .env
    echo "✅ Файл .env создан"
fi

# Проверяем зависимости
echo "📦 Проверяем зависимости..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt не найден"
    exit 1
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "🐍 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активируем виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install -r requirements.txt

# Инициализируем базу данных
echo "🗄️ Инициализируем базу данных..."
python -c "from app import app, db; app.app_context().push(); db.create_all()"

echo "✅ Готово к деплою!"
echo ""
echo "🎯 Следующие шаги:"
echo "1. Выберите хостинг (Heroku, Railway, PythonAnywhere, VPS)"
echo "2. Следуйте инструкциям в deploy_instructions.md"
echo "3. Не забудьте изменить SECRET_KEY в продакшене"
echo "4. Измените пароль администратора (admin/admin123)"
echo ""
echo "🔗 Проверьте работу: http://localhost:5000"
echo "🏥 Проверьте здоровье: http://localhost:5000/health"
