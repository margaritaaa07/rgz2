import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass

def create_postgres_db():
    """Создание базы данных в PostgreSQL"""
    
    print("🔧 Создание базы данных в PostgreSQL...")

    password = getpass.getpass("🔑 Введите пароль PostgreSQL (обычно тот, что при установке): ")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'vacation_planner_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📦 Создаем базу данных 'vacation_planner_db'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('vacation_planner_db')
            ))
            print("✅ База данных создана!")
        else:
            print("✅ База данных уже существует")
        
        cursor.close()
        conn.close()

        print("\n📊 Создаем таблицы...")
        
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=password,
            database='vacation_planner_db'
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(120) UNIQUE,
                password VARCHAR(200) NOT NULL,
                department VARCHAR(100),
                active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица 'users' создана")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                week_number INTEGER NOT NULL,
                year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, week_number, year)
            )
        """)
        print("✅ Таблица 'vacations' создана")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacations_user_id ON vacations(user_id)")

        from werkzeug.security import generate_password_hash
        admin_password_hash = generate_password_hash('admin123')
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("""
                INSERT INTO users (username, name, email, password, department, active, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                'admin',
                'Администратор',
                'admin@example.com',
                admin_password_hash,
                'Администрация',
                True,
                True
            ))
            print("👑 Создан администратор (admin / admin123)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎉 БАЗА ДАННЫХ POSTGRESQL ГОТОВА К РАБОТЕ!")
        print("=" * 50)
        print(f"\nДля подключения используйте строку:")
        print(f"postgresql://postgres:ваш_пароль@localhost:5432/vacation_planner_db")
        print("\n⚠️ Не забудьте заменить 'ваш_пароль' в app.py на реальный пароль!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nВозможные причины:")
        print("1. PostgreSQL не установлен или не запущен")
        print("2. Неправильный пароль")
        print("3. Пользователь 'postgres' не существует")
        return False

if __name__ == '__main__':
    create_postgres_db()