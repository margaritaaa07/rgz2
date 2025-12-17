import psycopg2
from werkzeug.security import generate_password_hash

def reset_admin_password():
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

        new_password = 'admin123'
        hashed_password = generate_password_hash(new_password)
        
        cursor.execute("""
            UPDATE users 
            SET password = %s 
            WHERE username = 'admin'
        """, (hashed_password,))
        
        conn.commit()
        
        print(f"✅ Пароль администратора сброшен:")
        print(f"   Логин: admin")
        print(f"   Пароль: {new_password}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    reset_admin_password()