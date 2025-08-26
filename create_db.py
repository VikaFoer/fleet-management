from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("🗄️ Создаем таблицы базы данных...")
    db.create_all()
    print("✅ Таблицы созданы успешно")
    
    # Создаем администратора
    print("👤 Создаем администратора...")
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
