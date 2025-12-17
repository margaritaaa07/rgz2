import psycopg2
from werkzeug.security import generate_password_hash

def create_new_admin():
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

        cursor.execute("DELETE FROM users WHERE username = 'admin'")

        admin_password = 'admin123'
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO users (username, name, email, password, department, active, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'admin',
            'Администратор',
            'admin@example.com',
            hashed_password,
            'Администрация',
            True,
            True
        ))
        
        conn.commit()
        
        print(f"✅ Новый администратор создан:")
        print(f"   Логин: admin")
        print(f"   Пароль: {admin_password}")
        print(f"   Email: admin@example.com")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    create_new_admin()