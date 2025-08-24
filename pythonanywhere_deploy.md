# 🚀 Деплой на PythonAnywhere

## Шаги:

1. **Создайте аккаунт на [PythonAnywhere](https://www.pythonanywhere.com)**

2. **Загрузите файлы:**
   - Перейдите в раздел "Files"
   - Загрузите все файлы проекта

3. **Создайте Web App:**
   - Перейдите в "Web" раздел
   - Нажмите "Add a new web app"
   - Выберите "Flask"
   - Выберите Python 3.11

4. **Настройте WSGI файл:**
   - Откройте файл `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   - Замените содержимое на:
   ```python
   import sys
   path = '/home/yourusername/fleet-management'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

5. **Установите зависимости:**
   - Перейдите в "Consoles" → "Bash"
   - Выполните:
   ```bash
   cd fleet-management
   pip install -r requirements.txt
   ```

6. **Создайте .env файл:**
   ```bash
   echo "SECRET_KEY=your-super-secret-key-here" > .env
   echo "DATABASE_URL=sqlite:///fleet.db" >> .env
   echo "FLASK_ENV=production" >> .env
   echo "FLASK_DEBUG=False" >> .env
   ```

7. **Инициализируйте базу данных:**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

8. **Перезапустите Web App:**
   - Вернитесь в "Web" раздел
   - Нажмите "Reload"

## Логин:
- **Логин:** admin
- **Пароль:** admin123
