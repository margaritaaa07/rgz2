import os
import re

class Config:
    SECRET_KEY = 'secret-key-change-in-production'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///vacations.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    MAX_VACATION_WEEKS = 4
    STUDENT_NAME = 'Бережная Маргарита Валерьевна'
    STUDENT_GROUP = 'ФБИ-33'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    USERNAME_REGEX = r'^[a-zA-Z0-9_.-]+$'
    PASSWORD_REGEX = r'^[a-zA-Z0-9@#$%^&+=!_.-]+$'
    
    @staticmethod
    def validate_username(username):
        """Валидация логина"""
        if not username or not re.match(Config.USERNAME_REGEX, username):
            return False, "Логин: только латинские буквы, цифры, _.-"
        return True, "OK"
    
    @staticmethod
    def validate_password(password):
        """Валидация пароля"""
        if not password or not re.match(Config.PASSWORD_REGEX, password):
            return False, "Пароль: только латинские буквы, цифры, спецсимволы"
        return True, "OK"