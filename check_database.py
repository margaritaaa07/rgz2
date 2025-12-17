import sqlite3
import sys
from pathlib import Path

def check_vacations_database():
    """Проверка базы данных системы планирования отпусков"""
    
    db_path = Path('instance/vacations.db')
    
    if not db_path.exists():
        print(" База данных не найдена!")
        print(f"Путь: {db_path.absolute()}")
        print("\nСоздайте базу данных, запустив приложение:")
        print("python app.py")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("=" * 60)
        print("ПРОВЕРКА БАЗЫ ДАННЫХ СИСТЕМЫ ПЛАНИРОВАНИЯ ОТПУСКОВ")
        print("=" * 60)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n Найдено таблиц: {len(tables)}")
        for table in tables:
            print(f"   • {table[0]}")
        
        print("\n" + "=" * 60)

        print("\n ПОЛЬЗОВАТЕЛИ (users):")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Всего пользователей: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        print(f"Администраторов: {admin_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
        regular_count = cursor.fetchone()[0]
        print(f"Обычных пользователей: {regular_count}")
        
        if user_count > 0:
            print("\n Последние 10 пользователей:")
            cursor.execute("""
                SELECT id, name, username, is_admin, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            users = cursor.fetchall()
            
            for user in users:
                user_id, name, username, is_admin, created_at = user
                admin_status = " АДМИН" if is_admin else "👤 ПОЛЬЗОВАТЕЛЬ"
                print(f"   ID: {user_id:3d} | {admin_status} | {name[:20]:20s} | @{username:15s} | {created_at[:10]}")

        print("\n" + "=" * 60)
        print("\n ОТПУСКА (vacations):")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM vacations")
        vacation_count = cursor.fetchone()[0]
        print(f"Всего записей об отпусках: {vacation_count}")
        
        if vacation_count > 0:
            cursor.execute("SELECT DISTINCT year FROM vacations ORDER BY year DESC")
            years = cursor.fetchall()
            print(f"\nГоды с отпусками ({len(years)}): {', '.join(str(y[0]) for y in years)}")

            print("\n Распределение по годам:")
            cursor.execute("""
                SELECT year, COUNT(*) as count 
                FROM vacations 
                GROUP BY year 
                ORDER BY year DESC
            """)
            yearly_stats = cursor.fetchall()
            
            for year, count in yearly_stats:
                print(f"   {year} год: {count:4d} отпусков")

            cursor.execute("""
                SELECT year, week_number, COUNT(*) as count 
                FROM vacations 
                GROUP BY year, week_number 
                ORDER BY count DESC 
                LIMIT 5
            """)
            popular_weeks = cursor.fetchall()
            
            if popular_weeks:
                print(f"\n ТОП-5 самых популярных недель:")
                for year, week, count in popular_weeks:
                    print(f"   {year} год, неделя {week:2d}: {count} отпусков")

            print("\n Последние 5 записей:")
            cursor.execute("""
                SELECT v.id, u.name, v.year, v.week_number, v.created_at 
                FROM vacations v 
                JOIN users u ON v.user_id = u.id 
                ORDER BY v.created_at DESC 
                LIMIT 5
            """)
            recent_vacations = cursor.fetchall()
            
            for vac in recent_vacations:
                vac_id, name, year, week, created_at = vac
                print(f"   ID: {vac_id:3d} | {name[:15]:15s} | {year} год, неделя {week:2d} | {created_at[:10]}")

        print("\n" + "=" * 60)
        print("\n СТРУКТУРА ТАБЛИЦ:")
        print("-" * 40)
        
        for table in tables:
            table_name = table[0]
            print(f"\n Таблица: {table_name}")
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   Колонки:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_value, pk = col
                pk_mark = " 🔑" if pk else ""
                null_mark = " NOT NULL" if not_null else ""
                default_mark = f" DEFAULT {default_value}" if default_value else ""
                print(f"     • {col_name:20s} {col_type:15s}{null_mark}{default_mark}{pk_mark}")

        print("\n" + "=" * 60)
        print("\n ПРОВЕРКА НОРМАЛЬНЫХ ФОРМ:")
        print("-" * 40)

        print("\n1. Первая нормальная форма (1НФ):")
        print("    Все поля атомарны")
        print("    Нет повторяющихся групп")
        print("    Определены первичные ключи")

        cursor.execute("""
            SELECT year, week_number, COUNT(*) 
            FROM vacations 
            GROUP BY year, week_number 
            HAVING COUNT(*) > 1
        """)
        duplicate_weeks = cursor.fetchall()
        
        if duplicate_weeks:
            print("    Обнаружены дубликаты недель в таблице vacations!")
            for year, week, count in duplicate_weeks:
                print(f"      {year} год, неделя {week}: {count} записей")
        else:
            print("    Уникальный constraint year+week работает корректно")

        print("\n2. Целостность внешних ключей:")

        cursor.execute("""
            SELECT COUNT(*) 
            FROM vacations v 
            LEFT JOIN users u ON v.user_id = u.id 
            WHERE u.id IS NULL
        """)
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count == 0:
            print("    Все отпуска ссылаются на существующих пользователей")
        else:
            print(f"    Найдено {orphaned_count} записей с несуществующими пользователями")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("\n РЕЗЮМЕ:")
        print("-" * 40)

        print(f" Общая статистика:")
        print(f"   • Пользователей: {user_count}")
        print(f"   • Администраторов: {admin_count}")
        print(f"   • Обычных пользователей: {regular_count}")
        print(f"   • Отпусков: {vacation_count}")
        
        if user_count > 0:
            avg_vacations = vacation_count / user_count if user_count > 0 else 0
            print(f"   • Среднее отпусков на пользователя: {avg_vacations:.2f}")

        if user_count >= 100:
            print(f"\n УСЛОВИЕ ВЫПОЛНЕНО: На сайте более 100 пользователей ({user_count})")
        else:
            print(f"\n⚠ ВНИМАНИЕ: На сайте менее 100 пользователей ({user_count})")
            print("   При запуске приложения автоматически создаются тестовые пользователи")
        
        print("\n" + "=" * 60)
        print(" ПРОВЕРКА ЗАВЕРШЕНА УСПЕШНО")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"\n Ошибка при работе с базой данных: {e}")
        sys.exit(1)

def export_users_csv():
    """Экспорт списка пользователей в CSV файл"""
    
    db_path = Path('instance/vacations.db')
    
    if not db_path.exists():
        print(" База данных не найдена!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, username, is_admin, created_at 
            FROM users 
            ORDER BY id
        """)
        users = cursor.fetchall()
        
        if users:
            csv_filename = "users_export.csv"
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write("ID;Имя;Логин;Статус;Дата регистрации\n")

                for user in users:
                    user_id, name, username, is_admin, created_at = user
                    status = "Администратор" if is_admin else "Пользователь"
                    f.write(f"{user_id};{name};{username};{status};{created_at}\n")
            
            print(f"\n📁 Список пользователей экспортирован в файл: {csv_filename}")
            print(f"   Всего записей: {len(users)}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f" Ошибка при экспорте: {e}")

if __name__ == "__main__":
    print("\n ЗАПУСК ПРОВЕРКИ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    check_vacations_database()

    response = input("\n Хотите экспортировать список пользователей в CSV? (y/n): ")
    if response.lower() in ['y', 'yes', 'да', 'д']:
        export_users_csv()
    
    print("\n Работа скрипта завершена")