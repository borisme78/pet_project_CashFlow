-- Користувачі
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Категорії доходів і витрат кожного користувача
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    UNIQUE (user_id, name)
);

-- Фінансові операції
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10, 2) NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    date DATE NOT NULL,
    description TEXT,
    category VARCHAR(50),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE
);