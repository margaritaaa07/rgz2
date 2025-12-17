from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vacations = db.relationship('Vacation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def is_valid_password(password):
        if not password or len(password) < 6:
            return False

        pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$'
        return bool(re.match(pattern, password))
    
    @staticmethod
    def is_valid_username(username):
        if not username or len(username) < 3 or len(username) > 50:
            return False

        pattern = r'^[a-zA-Z0-9_.-]+$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def is_valid_name(name):
        """
        Валидация имени (ФИО)
        """
        if not name or len(name) < 2 or len(name) > 100:
            return False

        pattern = r'^[А-Яа-яЁёA-Za-z\s\-]+$'
        return bool(re.match(pattern, name))
    
    def __repr__(self):
        return f'<User {self.username}>'


class Vacation(db.Model):
    
    __tablename__ = 'vacations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('year', 'week_number', name='_year_week_uc'),
    )
    
    @staticmethod
    def is_valid_week(week_number, year=None):
        try:
            week = int(week_number)
            return 1 <= week <= 53
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_year(year):
        try:
            year_int = int(year)
            return 2020 <= year_int <= 2030
        except (ValueError, TypeError):
            return False
    
    def __repr__(self):
        return f'<Vacation {self.year}-W{self.week_number}>'


def validate_form_data(data, is_admin=False):
    errors = []

    if 'name' in data:
        if not data['name']:
            errors.append("Имя обязательно для заполнения")
        elif not User.is_valid_name(data['name']):
            errors.append("Имя должно содержать только буквы, пробелы и дефисы (2-100 символов)")

    if 'username' in data:
        if not data['username']:
            errors.append("Логин обязателен для заполнения")
        elif not User.is_valid_username(data['username']):
            errors.append("Логин должен содержать только латинские буквы, цифры и символы: _ . - (3-50 символов)")

    if 'password' in data and data['password']:
        if not User.is_valid_password(data['password']):
            errors.append("Пароль должен содержать только латинские буквы, цифры и знаки препинания (минимум 6 символов)")

    if 'password' in data and 'confirm_password' in data:
        if data['password'] != data['confirm_password']:
            errors.append("Пароли не совпадают")

    if 'year' in data:
        if not Vacation.is_valid_year(data['year']):
            errors.append("Некорректный год")

    if 'week_number' in data:
        if not Vacation.is_valid_week(data['week_number']):
            errors.append("Номер недели должен быть от 1 до 53")
    
    return len(errors) == 0, errors