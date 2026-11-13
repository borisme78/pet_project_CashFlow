# Finance Tracker Dashboard

A simple web application for managing personal finances.

The application allows users to record income and expenses, view their transaction history, edit or delete transactions, and monitor their current financial balance.

## Features

* Add income and expense transactions
* View all transactions
* Edit existing transactions
* Delete transactions
* Calculate total income and expenses
* Calculate current balance
* Store data in PostgreSQL
* Validate transaction data
* Use environment variables for database configuration

## Technologies

* Python
* Flask
* PostgreSQL
* psycopg2
* python-dotenv
* HTML
* CSS
* Jinja2

## Project Structure

```text
finance-tracker/
├── app.py
├── database.py
├── init_db.sql
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── templates/
    ├── index.html
    ├── add_transaction.html
    └── edit_transaction.html
```
## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd finance-tracker
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate the virtual environment:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

Create a PostgreSQL database:

```sql
CREATE DATABASE finance_tracker;
```

Connect to the database and create the `transactions` table using the SQL script from:

```text
init_db.sql
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=finance_tracker
DB_USER=your_username
DB_PASSWORD=your_password
```

Use your own PostgreSQL username and password.

### 6. Run the application

Start the Flask application:

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```
## Database

The application uses PostgreSQL to store financial transactions.

### Transactions table

| Column        | Type            | Description            |
| ------------- | --------------- | ---------------------- |
| `id`          | `BIGSERIAL`     | Primary key            |
| `amount`      | `DECIMAL(10,2)` | Transaction amount     |
| `type`        | `VARCHAR(20)`   | `income` or `expense`  |
| `date`        | `DATE`          | Transaction date       |
| `description` | `TEXT`          | Additional information |
| `category`    | `VARCHAR(50)`   | Transaction category   |

The `type` column has a constraint that allows only two values:

```sql
CHECK (type IN ('income', 'expense'))
```

The application uses parameterized SQL queries to safely insert and update transaction data.
