#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
Запускается отдельно после деплоя
"""

import os
from app import app, db, init_database

if __name__ == '__main__':
    with app.app_context():
        print("🗄️ Инициализация базы данных...")
        init_database()
        print("✅ База данных успешно инициализирована!")
