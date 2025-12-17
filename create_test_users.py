# create_test_users.py
# Скрипт для создания тестовых пользователей

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash
from faker import Faker
import random

def create_test_users():
    """Создание тестовых пользователей"""
    with app.app_context():
        user_count = User.query.count()
        print(f"Текущее количество пользователей: {user_count}")
        
        if user_count >= 100:
            print("В базе уже 100 или более пользователей")
            return

        users_to_create = 100 - user_count
        print(f"Будет создано {users_to_create} тестовых пользователей")

        fake = Faker('ru_RU')
        departments = ['IT', 'HR', 'Финансы', 'Маркетинг', 'Продажи', 
                      'Поддержка', 'Разработка', 'Администрирование']
        
        new_users = []
        for i in range(users_to_create):
            username = f"user_{i+user_count+1:03d}"
            email = f"{username}@company.com"
            
            user = User(
                username=username,
                name=fake.name(),
                email=email,
                password=generate_password_hash('password123'),
                department=random.choice(departments),
                active=True,
                is_admin=False
            )
            new_users.append(user)

        db.session.add_all(new_users)
        db.session.commit()
        
        print(f"✅ Создано {len(new_users)} тестовых пользователей")
        print(f"✅ Всего пользователей в базе: {User.query.count()}")

if __name__ == '__main__':
    create_test_users()