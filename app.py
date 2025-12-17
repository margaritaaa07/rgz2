from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import csv
from io import StringIO
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24).hex()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/vacation_planner_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'pool_pre_ping': True,
}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

print("=" * 50)
print("🔄 ПОДКЛЮЧЕНИЕ К POSTGRESQL")
print(f"📊 База данных: vacation_planner_db")
print("=" * 50)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), default='Не указан')
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        return self.active
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

    vacations = db.relationship('Vacation', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.username}>'

class Vacation(db.Model):
    __tablename__ = 'vacations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'week_number', 'year', name='unique_user_week_year'),
    )
    
    def __repr__(self):
        return f'<Vacation user:{self.user_id} week:{self.week_number} year:{self.year}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Требуются права администратора', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_week_dates(year, week_number):
    """Возвращает даты начала и конца недели"""
    first_day = datetime(year, 1, 4)
    iso_offset = first_day.weekday()
    
    start_date = first_day + timedelta(days=(week_number - 1) * 7 - iso_offset)
    end_date = start_date + timedelta(days=6)
    
    return start_date.strftime('%d.%m'), end_date.strftime('%d.%m')

def get_current_week_info(year):
    """Получить информацию о всех неделях года"""
    weeks = []
    for week in range(1, 53):
        start_date, end_date = get_week_dates(year, week)
        weeks.append({
            'id': week,
            'number': week,
            'start_date': start_date,
            'end_date': end_date
        })
    return weeks

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        print(f"🔐 Попытка входа: username='{username}', password='{password}'")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"👤 Пользователь найден: {user.username}, активен: {user.active}")
            print(f"   Хэш в базе: {user.password[:50]}...")

            from werkzeug.security import check_password_hash
            is_correct = check_password_hash(user.password, password)
            print(f"   Проверка пароля: {is_correct}")
            
            if user and check_password_hash(user.password, password):
                if user.active:
                    login_user(user, remember=remember)
                    flash('Вы успешно вошли в систему!', 'success')
                    print(f"✅ Успешный вход для {username}")
                    return redirect(url_for('dashboard'))
                else:
                    flash('Аккаунт отключен', 'danger')
                    print(f"❌ Аккаунт отключен для {username}")
            else:
                flash('Неверный логин или пароль', 'danger')
                print(f"❌ Неверный пароль для {username}")
        else:
            flash('Неверный логин или пароль', 'danger')
            print(f"❌ Пользователь не найден: {username}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash('Пользователь с таким логином уже существует', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            user_count = User.query.count()
            is_admin = user_count == 0
            
            user = User(
                username=username,
                name=name,
                email=email if email else None,
                password=hashed_password,
                department=department if department else 'Не указан',
                active=True,
                is_admin=is_admin
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    year = request.args.get('year', type=int, default=datetime.now().year)
    
    weeks_info = get_current_week_info(year)
    
    vacations = Vacation.query.filter_by(year=year).all()
    
    week_vacations = {}
    user_vacations_ids = {}
    
    for vacation in vacations:
        week_vacations[vacation.week_number] = vacation
        if vacation.user_id == current_user.id:
            user_vacations_ids[vacation.week_number] = vacation.id
    
    for week in weeks_info:
        week_num = week['number']
        if week_num in week_vacations:
            vacation = week_vacations[week_num]
            week['occupied'] = True
            week['occupied_by'] = vacation.user_id
            week['occupied_by_name'] = vacation.user.name if vacation.user else 'Неизвестно'
            week['vacation_id'] = vacation.id
        else:
            week['occupied'] = False
            week['occupied_by'] = None
    
    selected_count = Vacation.query.filter_by(
        user_id=current_user.id, 
        year=year
    ).count()
    
    total_employees = User.query.filter_by(active=True).count()
    
    now = datetime.now()
    is_past_year = year < now.year
    
    return render_template('dashboard.html',
                         current_year=year,
                         weeks=weeks_info,
                         user_vacations=user_vacations_ids,
                         selected_count=selected_count,
                         remaining_count=4 - selected_count,
                         total_employees=total_employees,
                         is_past_year=is_past_year,
                         now=now)

@app.route('/toggle_vacation', methods=['POST'])
@login_required
def toggle_vacation():
    """Добавить/удалить неделю отпуска"""
    try:
        data = request.get_json()
        week = data.get('week')
        year = data.get('year')
        
        if not week or not year:
            return jsonify({'success': False, 'message': 'Не указана неделя или год'})

        existing = Vacation.query.filter_by(
            user_id=current_user.id,
            week_number=week,
            year=year
        ).first()
        
        if existing:
            db.session.delete(existing)
            action = 'удален'
        else:
            new_vacation = Vacation(
                user_id=current_user.id,
                week_number=week,
                year=year
            )
            db.session.add(new_vacation)
            action = 'добавлен'
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Отпуск на неделю {week} {action}'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/add_vacation_weeks', methods=['POST'])
@login_required
def add_vacation_weeks():
    """Добавить несколько недель отпуска"""
    try:
        data = request.get_json()
        weeks = data.get('weeks', [])
        year = data.get('year')
        
        if not weeks or not year:
            return jsonify({'success': False, 'message': 'Не указаны недели или год'})
        
        added = 0
        skipped = 0
        
        for week in weeks:
            existing = Vacation.query.filter_by(
                user_id=current_user.id,
                week_number=week,
                year=year
            ).first()
            
            if not existing:
                try:
                    new_vacation = Vacation(
                        user_id=current_user.id,
                        week_number=week,
                        year=year
                    )
                    db.session.add(new_vacation)
                    added += 1
                except:
                    skipped += 1
        
        db.session.commit()
        
        message = f'Добавлено {added} недель отпуска'
        if skipped > 0:
            message += f', {skipped} пропущено (дубликаты или ошибки)'
        
        return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/department_schedule')
@login_required
def department_schedule():
    """График отпусков отдела"""
    year = request.args.get('year', datetime.now().year, type=int)

    users = User.query.filter_by(
        department=current_user.department,
        active=True
    ).order_by(User.name).all()

    vacations = {}
    for user in users:
        user_vacations = Vacation.query.filter_by(
            user_id=user.id,
            year=year
        ).order_by(Vacation.week_number).all()
        vacations[user.id] = [v.week_number for v in user_vacations]

    now = datetime.now()
    start_of_year = datetime(year, 1, 1)
    if year == now.year:
        days_passed = (now - start_of_year).days
        current_week = days_passed // 7 + 1
    else:
        current_week = 0
    
    return render_template('department_schedule.html',
        year=year,
        users=users,
        vacations=vacations,
        current_user=current_user,
        current_week=current_week)

@app.route('/export_schedule')
@login_required
def export_schedule():
    """Экспорт графика отпусков"""
    year = request.args.get('year', datetime.now().year, type=int)
    format_type = request.args.get('format', 'csv')

    vacations = db.session.query(
        User.name,
        User.department,
        Vacation.week_number,
        Vacation.year
    ).join(
        Vacation, User.id == Vacation.user_id
    ).filter(
        Vacation.year == year,
        User.active == True
    ).order_by(
        User.department,
        User.name,
        Vacation.week_number
    ).all()
    
    if format_type == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ФИО', 'Отдел', 'Неделя', 'Год'])
        
        for vac in vacations:
            writer.writerow([vac.name, vac.department, vac.week_number, vac.year])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=vacations_{year}.csv"}
        )
    
    return "Формат не поддерживается", 400

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if current_password:
            user = User.query.get(current_user.id)
            
            if not check_password_hash(user.password, current_password):
                flash('Неверный текущий пароль', 'danger')
                return redirect('/profile')

            if new_password:
                password_hash = generate_password_hash(new_password)
                user.password = password_hash

        user = User.query.get(current_user.id)
        user.name = name
        user.email = email if email else None
        user.department = department if department else 'Не указан'
        
        db.session.commit()
        
        flash('Профиль обновлен', 'success')
        return redirect('/dashboard')

    user = User.query.get(current_user.id)

    user_vacations = Vacation.query.filter_by(user_id=current_user.id).all()

    vacations_by_year = {}
    for vacation in user_vacations:
        if vacation.year not in vacations_by_year:
            vacations_by_year[vacation.year] = []
        vacations_by_year[vacation.year].append(vacation)
    
    return render_template('profile.html', 
                         user=user, 
                         vacations_by_year=vacations_by_year)

@app.route('/calendar')
@login_required
def calendar():
    return redirect(url_for('dashboard'))

@app.route('/all_employees')
@login_required
def all_employees():
    employees = User.query.filter_by(active=True).order_by(User.name).all()

    employee_stats = []
    for employee in employees:
        vacation_count = Vacation.query.filter_by(user_id=employee.id).count()
        employee_stats.append({
            'user': employee,
            'vacation_count': vacation_count
        })
    
    return render_template('all_employees.html', 
                         employees=employee_stats,
                         total_employees=len(employees))

@app.route('/save_vacation', methods=['POST'])
@login_required
def save_vacation():
    if request.method == 'POST':
        year = request.form.get('year', type=int, default=datetime.now().year)
        week_number = request.form.get('week_number', type=int)
        
        if not week_number:
            flash('Не указан номер недели', 'danger')
            return redirect(url_for('dashboard', year=year))

        existing_vacation = Vacation.query.filter_by(
            week_number=week_number, 
            year=year
        ).first()
        
        if existing_vacation:
            flash(f'Неделя {week_number} уже занята другим сотрудником', 'danger')
            return redirect(url_for('dashboard', year=year))

        user_vacations_count = Vacation.query.filter_by(
            user_id=current_user.id, 
            year=year
        ).count()
        
        if user_vacations_count >= 4:
            flash('Вы уже выбрали максимальное количество недель (4)', 'danger')
            return redirect(url_for('dashboard', year=year))

        vacation = Vacation(
            user_id=current_user.id,
            week_number=week_number,
            year=year
        )
        
        db.session.add(vacation)
        db.session.commit()
        
        flash(f'Отпуск на неделю {week_number} успешно добавлен!', 'success')
    
    return redirect(url_for('dashboard', year=year))

@app.route('/cancel_vacation/<int:vacation_id>', methods=['POST'])
@login_required
def cancel_vacation(vacation_id):
    vacation = Vacation.query.get_or_404(vacation_id)

    if vacation.user_id != current_user.id:
        flash('Вы не можете отменить чужой отпуск', 'danger')
        return redirect(url_for('dashboard', year=vacation.year))
    
    year = vacation.year
    
    db.session.delete(vacation)
    db.session.commit()
    
    flash(f'Отпуск на неделю {vacation.week_number} отменен', 'info')
    return redirect(url_for('dashboard', year=year))

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_vacations = Vacation.query.count()
    current_year = datetime.now().year

    yearly_stats = []
    years = db.session.query(Vacation.year).distinct().all()
    for year_tuple in years:
        year = year_tuple[0]
        count = Vacation.query.filter_by(year=year).count()
        yearly_stats.append({
            'year': year,
            'count': count
        })
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_vacations=total_vacations,
                         yearly_stats=yearly_stats,
                         current_year=current_year)

@app.route('/admin/vacations')
@admin_required
def admin_vacations():
    year = request.args.get('year', type=int, default=datetime.now().year)

    vacations = Vacation.query.filter_by(year=year)\
        .order_by(Vacation.week_number)\
        .all()

    users_dict = {user.id: user for user in User.query.all()}
    
    return render_template('admin/vacations.html',
                         vacations=vacations,
                         users_dict=users_dict,
                         current_year=year,
                         now=datetime.now())

@app.route('/admin/create_vacation', methods=['GET', 'POST'])
@admin_required
def admin_create_vacation():
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        week_number = request.form.get('week_number', type=int)
        year = request.form.get('year', type=int)

        existing = Vacation.query.filter_by(
            week_number=week_number, 
            year=year
        ).first()
        
        if existing:
            flash(f'Неделя {week_number} уже занята', 'danger')
            return redirect(url_for('admin_create_vacation'))
        
        vacation = Vacation(
            user_id=user_id,
            week_number=week_number,
            year=year
        )
        
        db.session.add(vacation)
        db.session.commit()
        
        flash(f'Отпуск успешно создан', 'success')
        return redirect(url_for('admin_vacations', year=year))
    
    users = User.query.filter_by(active=True).order_by(User.name).all()
    current_year = datetime.now().year
    
    return render_template('admin/create_vacation.html',
                         users=users,
                         current_year=current_year)

@app.route('/admin/edit_vacation/<int:vacation_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_vacation(vacation_id):
    vacation = Vacation.query.get_or_404(vacation_id)
    
    if request.method == 'POST':
        week_number = request.form.get('week_number', type=int)
        year = request.form.get('year', type=int)

        existing = Vacation.query.filter(
            Vacation.week_number == week_number,
            Vacation.year == year,
            Vacation.id != vacation_id
        ).first()
        
        if existing:
            flash(f'Неделя {week_number} уже занята', 'danger')
            return redirect(url_for('admin_edit_vacation', vacation_id=vacation_id))
        
        vacation.week_number = week_number
        vacation.year = year
        vacation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Отпуск успешно обновлен', 'success')
        return redirect(url_for('admin_vacations', year=year))
    
    users = User.query.filter_by(active=True).order_by(User.name).all()
    
    return render_template('admin/edit_vacation.html',
                         vacation=vacation,
                         users=users)

@app.route('/admin/delete_vacation/<int:vacation_id>', methods=['POST'])
@admin_required
def admin_delete_vacation(vacation_id):
    vacation = Vacation.query.get_or_404(vacation_id)
    year = vacation.year
    
    db.session.delete(vacation)
    db.session.commit()
    
    flash('Отпуск успешно удален', 'success')
    return redirect(url_for('admin_vacations', year=year))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()

    users_with_stats = []
    for user in users:
        vacation_count = Vacation.query.filter_by(user_id=user.id).count()
        users_with_stats.append({
            'user': user,
            'vacation_count': vacation_count
        })
    
    return render_template('admin/users.html', users=users_with_stats)

@app.route('/admin/toggle_user/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Вы не можете отключить свой аккаунт', 'danger')
        return redirect(url_for('admin_users'))
    
    user.active = not user.active
    db.session.commit()
    
    status = 'активирован' if user.active else 'деактивирован'
    flash(f'Пользователь {user.name} {status}', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    total_users = User.query.count()
    active_users = User.query.filter_by(active=True).count()
    total_vacations = Vacation.query.count()

    years = db.session.query(Vacation.year).distinct().order_by(Vacation.year.desc()).all()
    yearly_stats = []
    for year_tuple in years:
        year = year_tuple[0]
        count = Vacation.query.filter_by(year=year).count()
        users_count = db.session.query(Vacation.user_id).filter_by(year=year).distinct().count()
        yearly_stats.append({
            'year': year,
            'count': count,
            'users_count': users_count
        })

    departments_stats = []
    departments = db.session.query(User.department).distinct().all()
    for dept_tuple in departments:
        if dept_tuple[0]:
            dept = dept_tuple[0]
            dept_users = User.query.filter_by(department=dept, active=True).count()
            dept_vacations = db.session.query(Vacation)\
                .join(User)\
                .filter(User.department == dept)\
                .count()
            departments_stats.append({
                'department': dept,
                'users_count': dept_users,
                'vacations_count': dept_vacations
            })
    
    return render_template('admin/statistics.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_vacations=total_vacations,
                         yearly_stats=yearly_stats,
                         departments_stats=departments_stats)

@app.route('/api/vacations/<int:vacation_id>/details')
@login_required
def api_vacation_details(vacation_id):
    vacation = Vacation.query.get_or_404(vacation_id)

    if not current_user.is_admin and vacation.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    return jsonify({
        'success': True,
        'vacation': {
            'id': vacation.id,
            'user_id': vacation.user_id,
            'user_name': vacation.user.name if vacation.user else None,
            'username': vacation.user.username if vacation.user else None,
            'week_number': vacation.week_number,
            'year': vacation.year,
            'created_at': vacation.created_at.isoformat() if vacation.created_at else None,
            'updated_at': vacation.updated_at.isoformat() if vacation.updated_at else None
        }
    })

def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("✅ Таблицы базы данных созданы/проверены")

            if User.query.count() == 0:
                admin = User(
                    username='admin',
                    name='Администратор',
                    email='admin@example.com',
                    password=generate_password_hash('admin123'),
                    department='Администрация',
                    active=True,
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("👑 Создан администратор (admin / admin123)")
            
            user_count = User.query.count()
            vacation_count = Vacation.query.count()
            
            print(f"👥 Пользователей: {user_count}")
            print(f"🏖️  Отпусков: {vacation_count}")

            if user_count < 10:
                print("💡 Совет: Запустите create_test_users.py для создания тестовых пользователей")
            
        except Exception as e:
            print(f"❌ Ошибка при инициализации базы данных: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)