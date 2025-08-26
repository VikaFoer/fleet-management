from app import app, db

with app.app_context():
    print("Создаем таблицы...")
    db.create_all()
    print("Таблицы созданы!")
    
    # Проверяем, что файл создался
    import os
    if os.path.exists('fleet.db'):
        print("✅ База данных создана!")
        print(f"Размер: {os.path.getsize('fleet.db')} байт")
    else:
        print("❌ База данных не создана!")
