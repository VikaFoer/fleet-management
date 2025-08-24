# 🚀 Деплой на Heroku

## Шаги:

1. **Установите Heroku CLI:**
   - Скачайте с: https://devcenter.heroku.com/articles/heroku-cli

2. **Войдите в Heroku:**
   ```bash
   heroku login
   ```

3. **Создайте приложение:**
   ```bash
   heroku create your-fleet-app-name
   ```

4. **Добавьте PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Установите переменные окружения:**
   ```bash
   heroku config:set SECRET_KEY="your-super-secret-key-here"
   heroku config:set FLASK_ENV=production
   heroku config:set FLASK_DEBUG=False
   ```

6. **Деплой:**
   ```bash
   git push heroku main
   ```

7. **Инициализируйте базу данных:**
   ```bash
   heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

8. **Откройте приложение:**
   ```bash
   heroku open
   ```

## Логин:
- **Логин:** admin
- **Пароль:** admin123
