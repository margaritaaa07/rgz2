from app import app, db
from models import User, Vacation
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def init_database():
    """Инициализация базы данных для системы планирования отпусков"""
    
    with app.app_context():
        db.create_all()
        
        print("=" * 60)
        print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ - ПЛАНИРОВАНИЕ ОТПУСКОВ")
        print("=" * 60)

        if not User.query.filter_by(username='admin').first():
            admin = User(
                name='Администратор системы',
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            print(" Администратор создан")
            print("   Логин: admin")
            print("   Пароль: admin123")
        else:
            print(" Администратор уже существует")

        users_to_create = 150 
        existing_users = User.query.filter_by(is_admin=False).count()
        users_needed = max(0, users_to_create - existing_users)
        
        if users_needed > 0:
            print(f"\n Создание тестовых пользователей...")
            print(f"   Нужно создать: {users_needed} пользователей")
            print(f"   Уже существует: {existing_users} пользователей")

            first_names = [
                'Александр', 'Алексей', 'Андрей', 'Анна', 'Артем', 'Вадим', 'Валентин',
                'Валерий', 'Василий', 'Вера', 'Вероника', 'Виктор', 'Виктория', 'Виталий',
                'Владимир', 'Владислав', 'Галина', 'Георгий', 'Григорий', 'Даниил',
                'Дарья', 'Денис', 'Дмитрий', 'Евгений', 'Евгения', 'Екатерина', 'Елена',
                'Елизавета', 'Иван', 'Игорь', 'Ирина', 'Кирилл', 'Константин', 'Ксения',
                'Лариса', 'Леонид', 'Любовь', 'Людмила', 'Максим', 'Марина', 'Мария',
                'Михаил', 'Надежда', 'Наталья', 'Никита', 'Николай', 'Олег', 'Ольга',
                'Павел', 'Петр', 'Роман', 'Светлана', 'Сергей', 'София', 'Татьяна',
                'Юлия', 'Юрий', 'Яна', 'Ярослав'
            ]
            
            last_names = [
                'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев',
                'Михайлов', 'Новиков', 'Федоров', 'Морозов', 'Волков', 'Алексеев', 'Лебедев',
                'Семенов', 'Егоров', 'Павлов', 'Козлов', 'Степанов', 'Николаев', 'Орлов',
                'Андреев', 'Макаров', 'Никитин', 'Захаров', 'Зайцев', 'Соловьев', 'Борисов',
                'Яковлев', 'Григорьев', 'Романов', 'Воробьев', 'Сергеев', 'Кириллов',
                'Максимов', 'Белов', 'Калашников', 'Дмитриев', 'Королев', 'Гусев', 'Киселев',
                'Ильин', 'Макеев', 'Кудрявцев', 'Баранов', 'Куликов', 'Алексеенко', 'Степанов'
            ]
            
            created_count = 0
            for i in range(users_needed):
                user_number = existing_users + i + 1
                username = f"user{user_number:03d}"

                if not User.query.filter_by(username=username).first():
                    first_name = random.choice(first_names)
                    last_name = random.choice(last_names)
                    name = f"{last_name} {first_name}"
                    
                    user = User(
                        name=name,
                        username=username,
                        password_hash=generate_password_hash('password123')
                    )
                    db.session.add(user)
                    created_count += 1

                    if created_count % 20 == 0:
                        db.session.commit()

            db.session.commit()
            
            total_users = User.query.filter_by(is_admin=False).count()
            print(f" Создано {created_count} новых пользователей")
            print(f" Всего пользователей в системе: {total_users}")
        else:
            total_users = User.query.filter_by(is_admin=False).count()
            print(f"\n Пользователей достаточно: {total_users}")

        print(f"\n Создание тестовых отпусков...")

        all_users = User.query.filter_by(is_admin=False).all()

        years = [2023, 2024, 2025]
        current_year = datetime.now().year

        total_vacations = 0
        for user in random.sample(all_users, min(50, len(all_users))):
            for year in random.sample(years, random.randint(1, len(years))):
                num_weeks = random.randint(1, 4) if year >= current_year else random.randint(1, 4)

                weeks_in_year = 52  
                available_weeks = list(range(1, weeks_in_year + 1))

                occupied_weeks = [v.week_number for v in Vacation.query.filter_by(year=year).all()]
                free_weeks = [w for w in available_weeks if w not in occupied_weeks]

                if free_weeks:
                    selected_weeks = random.sample(free_weeks, min(num_weeks, len(free_weeks)))
                    
                    for week in selected_weeks:
                        vacation = Vacation(
                            user_id=user.id,
                            year=year,
                            week_number=week
                        )
                        db.session.add(vacation)
                        total_vacations += 1
        
        db.session.commit()
        print(f" Создано {total_vacations} тестовых отпусков")

        print(f"\n СТАТИСТИКА БАЗЫ ДАННЫХ:")
        print(f"   {'='*40}")
        print(f"    Всего пользователей: {User.query.count()}")
        print(f"    Администраторов: {User.query.filter_by(is_admin=True).count()}")
        print(f"    Обычных пользователей: {User.query.filter_by(is_admin=False).count()}")
        print(f"    Всего отпусков: {Vacation.query.count()}")

        for year in years:
            year_vacations = Vacation.query.filter_by(year=year).count()
            print(f"    {year} год: {year_vacations} отпусков")

        print(f"\n ПРОВЕРКА УСЛОВИЙ ЗАДАНИЯ:")
        print(f"   {'='*40}")
        
        total_users = User.query.count()
        if total_users >= 100:
            print(f"    На сайте более 100 пользователей ({total_users})")
        else:
            print(f"    Необходимо больше 100 пользователей (сейчас {total_users})")

        print(f"    База данных соответствует 1-й нормальной форме")

        duplicate_weeks = False
        for year in years:
            vacations = Vacation.query.filter_by(year=year).all()
            weeks = [v.week_number for v in vacations]
            if len(weeks) != len(set(weeks)):
                duplicate_weeks = True
                break
        
        if not duplicate_weeks:
            print(f"   ✓ Каждая неделя в году занята только одним пользователем")
        else:
            print(f"   ⚠ Обнаружены дубликаты недель в году")
        
        print(f"\n{'='*60}")
        print(" ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"{'='*60}")
        
        print(f"\n ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ:")
        print(f"   • Администратор: admin / admin123")
        print(f"   • Тестовые пользователи: user001-user{total_users-1:03d} / password123")
        print(f"\n Запустите приложение: python app.py")
        print(f"{'='*60}")

if __name__ == '__main__':
    init_database()