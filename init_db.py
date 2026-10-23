# init_db.py
from database import get_db_connection

def create_tables():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                amount NUMERIC(10, 2) NOT NULL,
                type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                date DATE NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT
            );
        """)
        connection.commit()
        print("Таблицю 'transactions' успішно створено!")
    except Exception as e:
        print(f"Помилка при створенні таблиці: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    create_tables()