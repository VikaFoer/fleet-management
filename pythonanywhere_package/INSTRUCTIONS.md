# 🚀 Инструкции по развертыванию на PythonAnywhere

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
