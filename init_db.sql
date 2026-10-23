-- 1. Таблиця користувачів
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- 2. Таблиця транзакцій із прив'язкою до користувача (user_id)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    date TEXT NOT NULL,
    description TEXT,
    category TEXT,
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);



ALTER TABLE transactions 
ADD COLUMN user_id INT REFERENCES users(id) ON DELETE CASCADE;