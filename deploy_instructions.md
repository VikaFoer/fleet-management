# 🚀 Инструкции по развертыванию Fleet Management System

## Вариант 1: Heroku (Рекомендуется для начала)

### Подготовка:
1. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Создайте аккаунт на [Heroku](https://heroku.com)

### Деплой:
```bash
# Войдите в Heroku
heroku login

# Создайте новое приложение
heroku create your-fleet-app-name

# Добавьте PostgreSQL базу данных
heroku addons:create heroku-postgresql:mini

# Установите переменные окружения
heroku config:set SECRET_KEY="your-super-secret-key-here"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# Деплой
git add .
git commit -m "Initial deployment"
git push heroku main

# Запустите миграции базы данных
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Вариант 2: PythonAnywhere (Бесплатный)

### Подготовка:
1. Создайте аккаунт на [PythonAnywhere](https://www.pythonanywhere.com)
2. Загрузите файлы через Files или Git

### Настройка:
1. Создайте новое Web App
2. Выберите Flask и Python 3.11
3. Укажите путь к файлу: `/home/yourusername/fleet-management/app.py`
4. В WSGI файле добавьте:
```python
import sys
path = '/home/yourusername/fleet-management'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### Переменные окружения:
В файле `.env`:
```
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///fleet.db
FLASK_ENV=production
FLASK_DEBUG=False
```

## Вариант 3: Railway (Современный и простой)

### Подготовка:
1. Создайте аккаунт на [Railway](https://railway.app)
2. Подключите GitHub репозиторий

### Настройка:
1. Создайте новый проект
2. Подключите ваш GitHub репозиторий
3. Railway автоматически определит Python приложение
4. Добавьте переменные окружения в настройках проекта

### Переменные окружения:
```
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://...
FLASK_ENV=production
FLASK_DEBUG=False
```

## Вариант 4: VPS (DigitalOcean, AWS, etc.)

### Подготовка сервера:
```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python и зависимости
sudo apt install python3 python3-pip python3-venv nginx -y

# Создайте пользователя для приложения
sudo adduser fleetuser
sudo usermod -aG sudo fleetuser
```

### Настройка приложения:
```bash
# Переключитесь на пользователя
sudo su - fleetuser

# Клонируйте репозиторий
git clone https://github.com/yourusername/fleet-management.git
cd fleet-management

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env
echo "SECRET_KEY=your-super-secret-key-here" > .env
echo "DATABASE_URL=sqlite:///fleet.db" >> .env
echo "FLASK_ENV=production" >> .env
echo "FLASK_DEBUG=False" >> .env

# Инициализируйте базу данных
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Настройка Gunicorn:
```bash
# Создайте файл службы
sudo nano /etc/systemd/system/fleet.service
```

Содержимое файла:
```ini
[Unit]
Description=Fleet Management System
After=network.target

[Service]
User=fleetuser
WorkingDirectory=/home/fleetuser/fleet-management
Environment="PATH=/home/fleetuser/fleet-management/venv/bin"
ExecStart=/home/fleetuser/fleet-management/venv/bin/gunicorn --workers 3 --bind unix:fleet.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

### Настройка Nginx:
```bash
sudo nano /etc/nginx/sites-available/fleet
```

Содержимое:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/fleetuser/fleet-management/fleet.sock;
    }
}
```

```bash
# Активируйте сайт
sudo ln -s /etc/nginx/sites-available/fleet /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Запустите службу
sudo systemctl start fleet
sudo systemctl enable fleet
```

## 🔐 Безопасность

### Обязательно измените:
1. `SECRET_KEY` - сгенерируйте новый секретный ключ
2. Пароль администратора по умолчанию (`admin123`)
3. Настройте HTTPS (SSL сертификат)

### Генерация SECRET_KEY:
```python
import secrets
print(secrets.token_hex(32))
```

## 📊 Мониторинг

### Логи:
- Heroku: `heroku logs --tail`
- Railway: Встроенный мониторинг
- VPS: `sudo journalctl -u fleet -f`

### Здоровье приложения:
Добавьте endpoint для проверки:
```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()})
```

## 🚀 После деплоя

1. Проверьте работу приложения
2. Войдите как admin/admin123
3. Измените пароль администратора
4. Добавьте тестовые данные
5. Настройте резервное копирование базы данных

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь, что все переменные окружения установлены
3. Проверьте подключение к базе данных
4. Убедитесь, что порт 5000 (или PORT) доступен
