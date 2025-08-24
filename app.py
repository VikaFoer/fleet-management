from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import json

load_dotenv()

app = Flask(__name__)

# Настройка SECRET_KEY
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    # Генерируем SECRET_KEY если его нет
    import secrets
    secret_key = secrets.token_hex(32)
    print(f"Generated SECRET_KEY: {secret_key[:16]}...")
app.config['SECRET_KEY'] = secret_key

# Настройка базы данных
database_url = os.getenv('DATABASE_URL')
print(f"Database URL from env: {database_url}")

# Для Railway PostgreSQL
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url and (database_url.startswith('sqlite://') or database_url.startswith('postgresql://') or database_url.startswith('mysql://')):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fleet.db'

print(f"Final Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Автоматическая инициализация базы данных
def init_database():
    with app.app_context():
        try:
            db.create_all()
            
            # Создаем администратора по умолчанию
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
                print("✅ База данных инициализирована")
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            db.session.rollback()

# Инициализируем БД при запуске
init_database()

# Модели данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)  # Марка
    model = db.Column(db.String(50), nullable=False)  # Модель
    year = db.Column(db.Integer, nullable=False)  # Год
    engine_volume = db.Column(db.Float)  # Объем двигателя
    vin_code = db.Column(db.String(17), unique=True, nullable=False)  # VIN код
    license_plate = db.Column(db.String(20), unique=True, nullable=False)  # Госномер
    call_sign = db.Column(db.String(20), unique=True, nullable=False)  # Позывной
    mileage = db.Column(db.Integer, default=0)  # Пробег
    last_to_date = db.Column(db.Date)  # Дата последнего ТО (из журнала событий)
    breakdown_history = db.Column(db.Text)  # История поломок (из журнала событий)
    cost = db.Column(db.Float, default=0)  # Стоимость
    payback_weeks = db.Column(db.Integer)  # Недель до окупаемости
    payment_history = db.Column(db.Text)  # История платежей (из журнала событий)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CashFlow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)  # Дата
    income = db.Column(db.Float, default=0)  # Надходження
    expenses = db.Column(db.Float, default=0)  # Видатки
    balance = db.Column(db.Float, default=0)  # Сальдо
    credit_load = db.Column(db.Float, default=0)  # Кредитне навантаження
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contractor_type = db.Column(db.String(50), nullable=False)  # Тип контрагента
    subtype = db.Column(db.String(100))  # Підтип
    name = db.Column(db.String(200), nullable=False)  # Найменування
    phone = db.Column(db.String(20))  # Телефон
    location = db.Column(db.String(200))  # Геолокація
    notes = db.Column(db.Text)  # Примітки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventJournal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Дата события
    event_type = db.Column(db.String(50), nullable=False)  # ТИП события
    subtype = db.Column(db.String(100), nullable=False)  # ПІДТИП события
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))  # ОБ'ЄКТ (ТС)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'))  # Контрагент
    amount = db.Column(db.Float, default=0)  # Сумма
    description = db.Column(db.Text)  # Описание события
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehicle = db.relationship('Vehicle', backref='events')
    contractor = db.relationship('Contractor', backref='events')
    user = db.relationship('User', backref='events')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Константы для типов событий
EVENT_TYPES = [
    'інвестиції', 'видатки', 'надходження', 'державні'
]

EVENT_SUBTYPES = {
    'інвестиції': ['ЛІЗИНГ', 'ПОКУПКА', 'ГОТІВКА', 'ОБЛАДНАННЯ', 'КРЕДИТ'],
    'видатки': ['ПОСТАНОВКА НА ТО', 'ПОЛОМКА', 'ПЛАНОВИЙ РЕМОНТ', 'ПОЗАПЛАНОВИЙ РЕМОНТ', 'ЗАРПЛАТА', 'ЛОГІСТИКА', 'ДТП'],
    'надходження': ['ОРЕНДА', 'ЗАВДАТОК', 'КОМПЕНСАЦІЯ', 'ПРОДАЖ ЗА РОЗТЕРМІНУВАННЯМ', 'ПРОДАЖ'],
    'державні': ['ДОКУМЕНТИ', 'ШТРАФ', 'СТАХУВАННЯ', 'ПОДАТКИ']
}

def update_cashflow_from_event(event_date, event_type, event_subtype, amount, operation='add'):
    """
    Автоматически обновляет денежный поток при добавлении или удалении события
    operation: 'add' для добавления, 'remove' для удаления
    """
    # Получаем дату события
    event_date_only = event_date.date() if hasattr(event_date, 'date') else event_date
    
    # Ищем существующую запись денежного потока на эту дату
    cashflow_entry = CashFlow.query.filter_by(date=event_date_only).first()
    
    # Определяем множитель: +1 для добавления, -1 для удаления
    multiplier = 1 if operation == 'add' else -1
    adjusted_amount = amount * multiplier
    
    if cashflow_entry:
        # Обновляем существующую запись
        if event_type in ['надходження']:
            cashflow_entry.income += adjusted_amount
        elif event_type in ['видатки', 'державні']:
            cashflow_entry.expenses += adjusted_amount
        elif event_type in ['інвестиції']:
            # Проверяем подтип события для правильной классификации
            if event_subtype == 'КРЕДИТ':
                # Кредиты идут в кредитное нагружение
                cashflow_entry.credit_load += adjusted_amount
            else:
                # Остальные инвестиции идут в расходы
                cashflow_entry.expenses += adjusted_amount
        elif event_type in ['видатки', 'державні']:
            # Расходы и государственные платежи идут в расходы
            cashflow_entry.expenses += adjusted_amount
        elif event_type in ['надходження']:
            # Доходы идут в доходы
            cashflow_entry.income += adjusted_amount
        
        # Пересчитываем баланс
        cashflow_entry.balance = cashflow_entry.income - cashflow_entry.expenses - cashflow_entry.credit_load
        
        # Если все суммы стали 0, удаляем запись
        if cashflow_entry.income == 0 and cashflow_entry.expenses == 0 and cashflow_entry.credit_load == 0:
            db.session.delete(cashflow_entry)
    else:
        if operation == 'add':
            # Создаем новую запись только при добавлении
            income = amount if event_type in ['надходження'] else 0
            expenses = amount if event_type in ['видатки', 'державні'] else 0
            credit_load = amount if event_type in ['інвестиції'] and event_subtype == 'КРЕДИТ' else 0
            investment_expenses = amount if event_type in ['інвестиції'] and event_subtype != 'КРЕДИТ' else 0
            
            cashflow_entry = CashFlow(
                date=event_date_only,
                income=income,
                expenses=expenses + investment_expenses,
                credit_load=credit_load,
                balance=income - expenses - investment_expenses - credit_load
            )
            db.session.add(cashflow_entry)
    
    db.session.commit()
    return cashflow_entry

CONTRACTOR_TYPES = [
    'Постачальник', 'СТО', 'Орендар', 'Продавець', 'Лізингодавець', 
    'Банк', 'Покупець', 'Послуги', 'Державні установи'
]

# Маршруты
@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    except Exception as e:
        print(f"Error in index route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.utcnow(),
        'message': 'Application is running'
    })

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Невірне ім\'я користувача або пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    vehicles = Vehicle.query.all()
    recent_events = EventJournal.query.order_by(EventJournal.date.desc()).limit(10).all()
    
    # Статистика
    total_vehicles = len(vehicles)
    active_vehicles = len([v for v in vehicles if v.status == 'active'])
    
    # Последние события
    latest_events = EventJournal.query.join(Vehicle).order_by(EventJournal.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         vehicles=vehicles,
                         recent_events=recent_events,
                         total_vehicles=total_vehicles,
                         active_vehicles=active_vehicles,
                         latest_events=latest_events)

@app.route('/vehicles')
@login_required
def vehicles():
    vehicles = Vehicle.query.all()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        # Проверяем, не существует ли уже автомобиль с таким номером, позывным или VIN-кодом
        print(f"DEBUG: Checking for license_plate: '{request.form['license_plate']}'")
        print(f"DEBUG: Checking for call_sign: '{request.form['call_sign']}'")
        print(f"DEBUG: Checking for vin_code: '{request.form['vin_code']}'")
        
        existing_license = Vehicle.query.filter_by(license_plate=request.form['license_plate']).first()
        existing_call_sign = Vehicle.query.filter_by(call_sign=request.form['call_sign']).first()
        existing_vin = Vehicle.query.filter_by(vin_code=request.form['vin_code']).first()
        
        print(f"DEBUG: existing_license: {existing_license}")
        print(f"DEBUG: existing_call_sign: {existing_call_sign}")
        print(f"DEBUG: existing_vin: {existing_vin}")
        
        if existing_license:
            flash(f'Автомобіль з номером {request.form["license_plate"]} вже існує!', 'error')
            return render_template('add_vehicle.html')
        
        if existing_call_sign:
            flash(f'Автомобіль з позивним {request.form["call_sign"]} вже існує!', 'error')
            return render_template('add_vehicle.html')
        
        if existing_vin:
            flash(f'Автомобіль з VIN-кодом {request.form["vin_code"]} вже існує!', 'error')
            return render_template('add_vehicle.html')
        
        try:
            print(f"DEBUG: Creating vehicle with VIN: '{request.form['vin_code']}'")
            vehicle = Vehicle(
                brand=request.form['brand'],
                model=request.form['model'],
                year=int(request.form['year']),
                engine_volume=float(request.form['engine_volume']) if request.form['engine_volume'] else None,
                vin_code=request.form['vin_code'],
                license_plate=request.form['license_plate'],
                call_sign=request.form['call_sign'],
                mileage=int(request.form['mileage']) if request.form['mileage'] else 0,
                cost=float(request.form['cost']) if request.form['cost'] else 0
            )
            print(f"DEBUG: Vehicle object created, adding to session...")
            db.session.add(vehicle)
            print(f"DEBUG: Committing to database...")
            db.session.commit()
            print(f"DEBUG: Successfully committed!")
            flash('Транспортний засіб додано', 'success')
            return redirect(url_for('vehicles'))
        except Exception as e:
            print(f"DEBUG: Exception occurred: {type(e).__name__}: {str(e)}")
            db.session.rollback()
            flash(f'Помилка при додаванні автомобіля: {str(e)}', 'error')
            return render_template('add_vehicle.html')
    
    return render_template('add_vehicle.html')

@app.route('/events')
@login_required
def events():
    events = EventJournal.query.join(Vehicle).join(Contractor, isouter=True).order_by(EventJournal.date.desc()).all()
    return render_template('events.html', events=events)

@app.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        # Гибкий парсинг даты - поддерживает как YYYY-MM-DD, так и YYYY-MM-DDTHH:MM
        date_str = request.form['date']
        print(f"DEBUG: Received date string: '{date_str}'")
        try:
            if 'T' in date_str:
                event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            else:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # Если не удалось распарсить, используем текущую дату
            event_date = datetime.now()
            
        amount = float(request.form['amount']) if request.form['amount'] else 0
        
        event = EventJournal(
            date=event_date,
            event_type=request.form['event_type'],
            subtype=request.form['subtype'],
            vehicle_id=int(request.form['vehicle_id']) if request.form['vehicle_id'] else None,
            contractor_id=int(request.form['contractor_id']) if request.form['contractor_id'] else None,
            amount=amount,
            description=request.form['description'],
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Автоматически обновляем денежный поток
        if amount > 0:
            try:
                update_cashflow_from_event(event_date, request.form['event_type'], request.form['subtype'], amount)
                flash('Подію додано та оновлено грошовий потік', 'success')
            except Exception as e:
                flash(f'Подію додано, але помилка при оновленні грошового потоку: {str(e)}', 'warning')
        else:
            flash('Подію додано', 'success')
            
        return redirect(url_for('events'))
    
    vehicles = Vehicle.query.all()
    contractors = Contractor.query.all()
    return render_template('add_event.html', 
                         vehicles=vehicles, 
                         contractors=contractors,
                         event_types=EVENT_TYPES,
                         event_subtypes=EVENT_SUBTYPES)

@app.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = EventJournal.query.get_or_404(event_id)
    
    try:
        # Корректируем денежный поток при удалении события
        if event.amount > 0:
            update_cashflow_from_event(event.date, event.event_type, event.subtype, event.amount, 'remove')
        
        # Удаляем событие
        db.session.delete(event)
        db.session.commit()
        flash('Подію видалено та оновлено грошовий потік', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Помилка при видаленні події: {str(e)}', 'error')
    
    return redirect(url_for('events'))

@app.route('/events/by_contractor/<int:contractor_id>')
@login_required
def events_by_contractor(contractor_id):
    contractor = Contractor.query.get_or_404(contractor_id)
    events = EventJournal.query.filter_by(contractor_id=contractor_id).order_by(EventJournal.date.desc()).all()
    return render_template('events_by_contractor.html', events=events, contractor=contractor)

@app.route('/events/by_vehicle/<int:vehicle_id>')
@login_required
def events_by_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    events = EventJournal.query.filter_by(vehicle_id=vehicle_id).order_by(EventJournal.date.desc()).all()
    return render_template('events_by_vehicle.html', events=events, vehicle=vehicle)

@app.route('/contractors')
@login_required
def contractors():
    contractors = Contractor.query.all()
    return render_template('contractors.html', contractors=contractors)

@app.route('/contractors/add', methods=['GET', 'POST'])
@login_required
def add_contractor():
    if request.method == 'POST':
        contractor = Contractor(
            contractor_type=request.form['contractor_type'],
            subtype=request.form['subtype'],
            name=request.form['name'],
            phone=request.form['phone'],
            location=request.form['location'],
            notes=request.form['notes']
        )
        db.session.add(contractor)
        db.session.commit()
        flash('Контрагента додано', 'success')
        return redirect(url_for('contractors'))
    
    return render_template('add_contractor.html', contractor_types=CONTRACTOR_TYPES)

@app.route('/cashflow')
@login_required
def cashflow():
    cashflow_entries = CashFlow.query.order_by(CashFlow.date.desc()).all()
    return render_template('cashflow.html', cashflow_entries=cashflow_entries)

@app.route('/cashflow/add', methods=['GET', 'POST'])
@login_required
def add_cashflow():
    if request.method == 'POST':
        # Проверяем, существует ли уже запись на эту дату
        entry_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        existing_entry = CashFlow.query.filter_by(date=entry_date).first()
        
        if existing_entry:
            # Обновляем существующую запись
            existing_entry.income += float(request.form['income']) if request.form['income'] else 0
            existing_entry.expenses += float(request.form['expenses']) if request.form['expenses'] else 0
            existing_entry.credit_load += float(request.form['credit_load']) if request.form['credit_load'] else 0
            existing_entry.balance = existing_entry.income - existing_entry.expenses - existing_entry.credit_load
            flash('Запис оновлено', 'success')
        else:
            # Создаем новую запись
            cashflow = CashFlow(
                date=entry_date,
                income=float(request.form['income']) if request.form['income'] else 0,
                expenses=float(request.form['expenses']) if request.form['expenses'] else 0,
                credit_load=float(request.form['credit_load']) if request.form['credit_load'] else 0
            )
            # Автоматический расчет сальдо
            cashflow.balance = cashflow.income - cashflow.expenses - cashflow.credit_load
            db.session.add(cashflow)
            flash('Запис додано', 'success')
        
        db.session.commit()
        return redirect(url_for('cashflow'))
    
    return render_template('add_cashflow.html')

@app.route('/documents')
@login_required
def documents():
    return render_template('documents.html')

@app.route('/generate_report/<report_type>')
@login_required
def generate_report(report_type):
    if report_type == 'vehicles':
        vehicles = Vehicle.query.all()
        return generate_vehicles_report(vehicles)
    elif report_type == 'events':
        events = EventJournal.query.join(Vehicle).join(Contractor, isouter=True).all()
        return generate_events_report(events)
    elif report_type == 'cashflow':
        cashflow_entries = CashFlow.query.all()
        return generate_cashflow_report(cashflow_entries)
    
    return redirect(url_for('documents'))

def generate_vehicles_report(vehicles):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    
    story.append(Paragraph("Отчет по транспортным средствам", title_style))
    story.append(Spacer(1, 12))
    
    data = [['Позывной', 'Марка', 'Модель', 'Год', 'Гос. номер', 'Пробег', 'Стоимость', 'Статус']]
    for vehicle in vehicles:
        data.append([
            vehicle.call_sign,
            vehicle.brand,
            vehicle.model,
            str(vehicle.year),
            vehicle.license_plate,
            f"{vehicle.mileage:,} км",
            f"{vehicle.cost:,.2f} ₽",
            vehicle.status
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    doc.build(story)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='vehicles_report.pdf')

def generate_events_report(events):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    
    story.append(Paragraph("Отчет по событиям", title_style))
    story.append(Spacer(1, 12))
    
    data = [['Дата', 'Тип', 'Подтип', 'ТС', 'Контрагент', 'Сумма', 'Описание']]
    for event in events:
        data.append([
            event.date.strftime('%d.%m.%Y'),
            event.event_type,
            event.subtype,
            event.vehicle.call_sign if event.vehicle else '-',
            event.contractor.name if event.contractor else '-',
            f"{event.amount:,.2f} ₽",
            event.description[:50] + '...' if event.description and len(event.description) > 50 else event.description or '-'
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    doc.build(story)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='events_report.pdf')

def generate_cashflow_report(cashflow_entries):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    
    story.append(Paragraph("Отчет по денежным потокам", title_style))
    story.append(Spacer(1, 12))
    
    data = [['Дата', 'Надходження', 'Видатки', 'Кредитне навантаження', 'Сальдо']]
    for entry in cashflow_entries:
        data.append([
            entry.date.strftime('%d.%m.%Y'),
            f"{entry.income:,.2f} ₽",
            f"{entry.expenses:,.2f} ₽",
            f"{entry.credit_load:,.2f} ₽",
            f"{entry.balance:,.2f} ₽"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    doc.build(story)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='cashflow_report.pdf')

if __name__ == '__main__':
    # Для локальной разработки
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# Инициализация базы данных только при запуске
def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            # Создаем администратора по умолчанию
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
                print("✅ База данных инициализирована успешно")
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            db.session.rollback() 