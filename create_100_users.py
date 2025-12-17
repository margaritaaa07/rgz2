import psycopg2
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

def create_100_users():
    
    print("=" * 60)
    print("👥 СОЗДАНИЕ 100 СЛУЧАЙНЫХ СОТРУДНИКОВ")
    print("=" * 60)

    password = 'postgres'  
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=password,
            database='vacation_planner_db'
        )
        
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        current_count = cursor.fetchone()[0]
        
        print(f"📊 Текущее количество пользователей в базе: {current_count}")

        if current_count >= 100:
            print("✅ В базе уже есть 100+ пользователей!")
            print(f"   👤 Администратор: admin / admin123")
            return
        
        users_to_create = 100 - current_count
        print(f"📝 Будет создано {users_to_create} новых пользователей...")

        male_first_names = [
            'Александр', 'Алексей', 'Андрей', 'Антон', 'Артем', 'Борис', 'Вадим', 
            'Валентин', 'Валерий', 'Василий', 'Виктор', 'Виталий', 'Владимир', 
            'Владислав', 'Геннадий', 'Георгий', 'Григорий', 'Даниил', 'Денис', 
            'Дмитрий', 'Евгений', 'Егор', 'Иван', 'Игорь', 'Илья', 'Кирилл', 
            'Константин', 'Лев', 'Леонид', 'Максим', 'Марк', 'Матвей', 'Михаил', 
            'Никита', 'Николай', 'Олег', 'Павел', 'Петр', 'Роман', 'Руслан', 
            'Сергей', 'Станислав', 'Степан', 'Тимофей', 'Федор', 'Юрий', 'Ярослав'
        ]
        
        female_first_names = [
            'Александра', 'Алена', 'Алина', 'Алиса', 'Алла', 'Анастасия', 'Ангелина',
            'Анна', 'Валентина', 'Валерия', 'Варвара', 'Вера', 'Вероника', 'Виктория',
            'Галина', 'Дарья', 'Диана', 'Евгения', 'Екатерина', 'Елена', 'Елизавета',
            'Жанна', 'Злата', 'Инна', 'Ирина', 'Карина', 'Кира', 'Ксения', 'Лариса',
            'Лидия', 'Любовь', 'Людмила', 'Маргарита', 'Марина', 'Мария', 'Надежда',
            'Наталья', 'Нина', 'Оксана', 'Олеся', 'Ольга', 'Полина', 'Раиса', 'Светлана',
            'София', 'Тамара', 'Татьяна', 'Ульяна', 'Юлия', 'Яна'
        ]
        
        last_names = [
            'Иванов', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Петров', 'Соколов',
            'Михайлов', 'Новиков', 'Федоров', 'Морозов', 'Волков', 'Алексеев', 'Лебедев',
            'Семенов', 'Егоров', 'Павлов', 'Козлов', 'Степанов', 'Николаев', 'Орлов',
            'Андреев', 'Макаров', 'Никитин', 'Захаров', 'Зайцев', 'Соловьев', 'Борисов',
            'Яковлев', 'Григорьев', 'Романов', 'Воробьев', 'Сергеев', 'Кузьмин', 'Фролов',
            'Александров', 'Дмитриев', 'Королев', 'Гусев', 'Киселев', 'Ильин', 'Максимов',
            'Поляков', 'Сорокин', 'Виноградов', 'Ковалев', 'Белов', 'Медведев', 'Антонов',
            'Тарасов', 'Жуков', 'Баранов', 'Филиппов', 'Комаров', 'Давыдов', 'Беляев',
            'Герасимов', 'Богданов', 'Осипов', 'Сидоров', 'Матвеев', 'Титов', 'Марков',
            'Миронов', 'Крылов', 'Куликов', 'Карпов', 'Власов', 'Мельников', 'Денисов',
            'Гаврилов', 'Тихонов', 'Казаков', 'Афанасьев', 'Данилов', 'Савельев', 'Тимофеев',
            'Фомин', 'Чернов', 'Абрамов', 'Мартынов', 'Ефимов', 'Щербаков', 'Назаров',
            'Калинин', 'Исаев', 'Чернышев', 'Быков', 'Маслов', 'Родионов', 'Коновалов',
            'Лазарев', 'Воронин', 'Климов', 'Филатов', 'Пономарев', 'Голубев', 'Кудрявцев',
            'Прохоров', 'Наумов', 'Потапов', 'Журавлев', 'Овчинников', 'Трофимов', 'Леонов',
            'Соболев', 'Ермаков', 'Колесников', 'Гончаров', 'Емельянов', 'Никифоров',
            'Грачев', 'Котов', 'Гришин', 'Ефремов', 'Архипов', 'Громов', 'Кириллов',
            'Малышев', 'Панов', 'Моисеев', 'Румянцев', 'Акимов', 'Кондратьев', 'Бирюков',
            'Горбунов', 'Анисимов', 'Еремин', 'Тихомиров', 'Галкин', 'Лукьянов', 'Михеев',
            'Скворцов', 'Юдин', 'Белоусов', 'Нестеров', 'Симонов', 'Прокофьев', 'Харитонов',
            'Князев', 'Цветков', 'Левин', 'Митрофанов', 'Воронов', 'Ермолаев', 'Гуляев',
            'Петухов', 'Лапин', 'Семин', 'Злобин', 'Костин', 'Шестаков', 'Яшин', 'Рыбаков'
        ]

        departments = [
            'IT-отдел', 'Отдел разработки', 'Отдел тестирования', 'Отдел DevOps',
            'Отдел кадров (HR)', 'Бухгалтерия', 'Финансовый отдел', 'Планово-экономический отдел',
            'Отдел маркетинга', 'Отдел рекламы', 'Отдел продаж', 'Отдел закупок',
            'Отдел логистики', 'Склад', 'Производственный отдел', 'Технический отдел',
            'Отдел качества', 'Юридический отдел', 'Отдел безопасности', 'Административный отдел',
            'Клиентский отдел', 'Техническая поддержка', 'Отдел аналитики', 'Отдел исследований'
        ]

        created_users = []
        used_emails = set()  
        
        for i in range(users_to_create):
            is_male = random.choice([True, False])
            
            if is_male:
                first_name = random.choice(male_first_names)
                patronymic = random.choice(['Александрович', 'Алексеевич', 'Андреевич', 
                                           'Дмитриевич', 'Сергеевич', 'Иванович', 
                                           'Владимирович', 'Викторович'])
            else:
                first_name = random.choice(female_first_names)
                patronymic = random.choice(['Александровна', 'Алексеевна', 'Андреевна',
                                           'Дмитриевна', 'Сергеевна', 'Ивановна',
                                           'Владимировна', 'Викторовна'])
            
            last_name = random.choice(last_names)

            full_name = f"{last_name} {first_name} {patronymic}"

            username = f"{first_name.lower()}.{last_name.lower()}{i+1}"

            base_email = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{base_email}{i+100}@company.com" 

            if len(email) > 120:
                email = f"{base_email[:50]}{i+100}@company.com"

            if email in used_emails:
                email = f"{base_email}{random.randint(1000, 9999)}@company.com"
            
            used_emails.add(email)

            department = random.choice(departments)

            password_hash = generate_password_hash('password123')

            is_admin = False

            active = random.random() > 0.05

            created_users.append((
                username, full_name, email, password_hash, 
                department, active, is_admin
            ))

            if (i + 1) % 25 == 0:
                print(f"   Создано {i + 1} пользователей...")

        print("\n💾 Сохранение пользователей в базу данных...")
        
        success_count = 0
        error_count = 0
        
        for user_data in created_users:
            try:
                cursor.execute("""
                    INSERT INTO users (username, name, email, password, department, active, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, user_data)
                success_count += 1
            except psycopg2.errors.UniqueViolation:
                error_count += 1
                print(f"   ⚠️  Пропущен дубликат: {user_data[0]}")
                continue
            except Exception as e:
                print(f"   ⚠️  Ошибка при создании {user_data[0]}: {e}")
                error_count += 1
                continue
        
        conn.commit()
        
        print(f"   ✅ Успешно создано: {success_count} пользователей")
        if error_count > 0:
            print(f"   ⚠️  Пропущено из-за ошибок: {error_count} пользователей")

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
        admin_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE active = TRUE")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM users 
            WHERE is_admin = FALSE
            GROUP BY department 
            ORDER BY count DESC
        """)
        
        departments_stats = cursor.fetchall()
        
        cursor.execute("""
            SELECT username, name, email FROM users 
            WHERE is_admin = FALSE 
            ORDER BY id 
            LIMIT 5
        """)
        sample_users = cursor.fetchall()
        
        print("\n" + "=" * 60)
        print("✅ ПОЛЬЗОВАТЕЛИ УСПЕШНО СОЗДАНЫ!")
        print("=" * 60)
        
        print(f"\n📊 СТАТИСТИКА БАЗЫ ДАННЫХ:")
        print(f"   👤 Всего пользователей: {total_users}")
        print(f"   👑 Администраторов: {admin_count}")
        print(f"   👥 Обычных сотрудников: {total_users - admin_count}")
        print(f"   ✅ Активных пользователей: {active_count}")
        print(f"   ❌ Неактивных пользователей: {total_users - active_count}")
        
        print(f"\n🏢 РАСПРЕДЕЛЕНИЕ ПО ОТДЕЛАМ:")
        for dept, count in departments_stats[:10]:  
            print(f"   - {dept}: {count} сотрудников")
        
        if len(departments_stats) > 10:
            print(f"   ... и еще {len(departments_stats) - 10} отделов")
        
        print(f"\n🔐 ТЕСТОВЫЕ УЧЕТНЫЕ ЗАПИСИ:")
        print(f"   👑 Администратор: admin / admin123")
        
        if sample_users:
            print(f"\n👤 ПРИМЕРЫ СОЗДАННЫХ СОТРУДНИКОВ:")
            for idx, (username, name, email) in enumerate(sample_users, 1):
                print(f"   {idx}. {name}")
                print(f"      Логин: {username} / password123")
                print(f"      Email: {email}")
        
        print(f"\n📧 Все пользователи имеют пароль: password123")

        cursor.execute("SELECT username, name, email, department, active FROM users ORDER BY id")
        all_users = cursor.fetchall()
        
        with open('users_list.txt', 'w', encoding='utf-8') as f:
            f.write("СПИСОК СОТРУДНИКОВ ДЛЯ СИСТЕМЫ ПЛАНИРОВАНИЯ ОТПУСКОВ\n")
            f.write("=" * 60 + "\n")
            f.write(f"Всего сотрудников: {total_users}\n")
            f.write(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("👑 АДМИНИСТРАТОРЫ:\n")
            for user in all_users:
                if user[0] == 'admin':  
                    f.write(f"  • {user[1]} | Логин: {user[0]} | Email: {user[2]}\n")
            
            f.write("\n👥 СОТРУДНИКИ:\n")
            for i, user in enumerate(all_users, 1):
                if user[0] != 'admin':  
                    status = "✅ АКТИВЕН" if user[4] else "❌ НЕАКТИВЕН"
                    f.write(f"  {i:3}. {user[1]:40} | {user[0]:25} | {user[2]:30} | {user[3]:30} | {status}\n")
        
        print(f"\n💾 Список пользователей сохранен в файл: users_list.txt")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании пользователей: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_some_vacations():
    """Добавляем тестовые отпуска для проверки функционала"""
    
    print("\n" + "=" * 60)
    print("🏖️  СОЗДАНИЕ ТЕСТОВЫХ ОТПУСКОВ")
    print("=" * 60)
    
    try:
        password = 'postgres'  
        
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=password,
            database='vacation_planner_db'
        )
        
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE is_admin = FALSE AND active = TRUE ORDER BY RANDOM() LIMIT 20")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("⚠️  Нет активных пользователей для создания отпусков")
            cursor.close()
            conn.close()
            return

        vacations_added = 0
        current_year = datetime.now().year
        
        for user_id in user_ids:
            for year in [current_year - 1, current_year, current_year + 1]:
                weeks_count = random.randint(2, 4)
                all_weeks = list(range(1, 53))
                random.shuffle(all_weeks)
                weeks = all_weeks[:weeks_count]
                
                for week in weeks:
                    try:
                        cursor.execute("""
                            INSERT INTO vacations (user_id, week_number, year)
                            VALUES (%s, %s, %s)
                        """, (user_id, week, year))
                        vacations_added += 1
                    except:
                        pass
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM vacations")
        total_vacations = cursor.fetchone()[0]
        
        print(f"✅ Добавлено тестовых отпусков: {vacations_added}")
        print(f"🏖️  Всего отпусков в базе: {total_vacations}")

        cursor.execute("""
            SELECT year, COUNT(*) as count 
            FROM vacations 
            GROUP BY year 
            ORDER BY year
        """)
        
        print(f"\n📅 РАСПРЕДЕЛЕНИЕ ОТПУСКОВ ПО ГОДАМ:")
        for year, count in cursor.fetchall():
            print(f"   - {year} год: {count} недель отпуска")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Ошибка при создании отпусков: {e}")

if __name__ == '__main__':
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password='postgres',  
            database='vacation_planner_db'
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username != 'admin'")
        cursor.execute("DELETE FROM vacations")  
        conn.commit()
        cursor.close()
        conn.close()
        print("🗑️  Старые пользователи (кроме админа) удалены")
    except:
        print("⚠️  Не удалось очистить старых пользователей, продолжаем...")

    if create_100_users():
        add_some_vacations()
    
    print("\n" + "=" * 60)
    print("🎉 ВСЕ ГОТОВО К ТЕСТИРОВАНИЮ!")
    print("=" * 60)
    print("\nТеперь в вашей системе есть:")
    print("   ✅ 100+ случайных сотрудников")
    print("   ✅ Тестовые отпуска на разные годы")
    print("   ✅ Администратор для управления")
    print("\nЗапустите приложение: python app.py")
    print("И войдите как администратор: admin / admin123")
    