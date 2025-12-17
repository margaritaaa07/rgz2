import psycopg2
from werkzeug.security import generate_password_hash
import getpass

def full_reset():
    print("=" * 60)
    print("🔄 ПОЛНЫЙ СБРОС СИСТЕМЫ АВТОРИЗАЦИИ")
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

        cursor.execute("DELETE FROM vacations")
        cursor.execute("DELETE FROM users")
        print("🗑️  Все пользователи удалены")

        cursor.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE vacations_id_seq RESTART WITH 1")

        admin_password = 'admin123'
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO users (username, name, email, password, department, active, is_admin, created_at)
            VALUES ('admin', 'Администратор', 'admin@company.com', %s, 'Администрация', TRUE, TRUE, NOW())
        """, (hashed_password,))

        test_password = 'password123'
        test_hash = generate_password_hash(test_password)
        
        cursor.execute("""
            INSERT INTO users (username, name, email, password, department, active, is_admin, created_at)
            VALUES ('test.user', 'Тестовый Пользователь', 'test@company.com', %s, 'IT-отдел', TRUE, FALSE, NOW())
        """, (test_hash,))
        
        conn.commit()

        cursor.execute("SELECT username, name, is_admin FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print("\n✅ ПОЛЬЗОВАТЕЛИ СОЗДАНЫ:")
        for user in users:
            print(f"  • {user[1]} ({user[0]}) - {'👑 Админ' if user[2] else '👤 Пользователь'}")
        
        print("\n" + "=" * 60)
        print("🔐 ДАННЫЕ ДЛЯ ВХОДА:")
        print(f"   👑 АДМИНИСТРАТОР:")
        print(f"      Логин: admin")
        print(f"      Пароль: {admin_password}")
        print(f"      Email: admin@company.com")
        print()
        print(f"   👤 ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ:")
        print(f"      Логин: test.user")
        print(f"      Пароль: {test_password}")
        print(f"      Email: test@company.com")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    full_reset()