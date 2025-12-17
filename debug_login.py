import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

def debug_login():
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
        
        print("=" * 60)
        print("🔍 ДЕБАГ АВТОРИЗАЦИИ")
        print("=" * 60)

        cursor.execute("SELECT id, username, name, password, active, is_admin FROM users")
        users = cursor.fetchall()
        
        print("\n👥 ВСЕ ПОЛЬЗОВАТЕЛИ:")
        for user in users:
            print(f"  ID: {user[0]}, Username: '{user[1]}', Name: '{user[2]}', Active: {user[4]}, Admin: {user[5]}")
            print(f"     Password hash: {user[3][:50]}...")

            if check_password_hash(user[3], 'admin123'):
                print(f"     ✅ Пароль 'admin123' ПОДХОДИТ!")
            else:
                print(f"     ❌ Пароль 'admin123' НЕ ПОДХОДИТ")

            if check_password_hash(user[3], ''):
                print(f"     ⚠️  Пустой пароль ПОДХОДИТ!")

            if user[3] == 'admin123':
                print(f"     ⚠️  Пароль хранится в открытом виде!")
            print()

        print("\n🔄 СОЗДАЕМ НОВОГО АДМИНИСТРАТОРА...")

        cursor.execute("DELETE FROM users WHERE username = 'admin'")

        admin_password = 'admin123'
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO users (username, name, email, password, department, active, is_admin, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (
            'admin',
            'Администратор',
            'admin@company.com',
            hashed_password,
            'Администрация',
            True,
            True
        ))
        
        admin_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Администратор создан:")
        print(f"   ID: {admin_id}")
        print(f"   Username: admin")
        print(f"   Password: {admin_password}")
        print(f"   Hash: {hashed_password[:50]}...")

        cursor.execute("SELECT password FROM users WHERE id = %s", (admin_id,))
        new_hash = cursor.fetchone()[0]
        
        if check_password_hash(new_hash, admin_password):
            print(f"✅ Проверка: пароль '{admin_password}' корректно работает!")
        else:
            print(f"❌ Ошибка: пароль не работает!")
            print(f"   Ожидался хэш для '{admin_password}'")
            print(f"   Получен хэш: {new_hash[:50]}...")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎯 Теперь попробуйте войти:")
        print("   Логин: admin")
        print("   Пароль: admin123")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_login()