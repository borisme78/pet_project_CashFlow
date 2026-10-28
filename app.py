import os
from datetime import datetime
from functools import wraps

import flask
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection

# ==================== 1. КОНФІГУРАЦІЯ ТА ІНІЦІАЛІЗАЦІЯ ====================

load_dotenv()

app = flask.Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application!")

ALLOWED_TYPES = {"income", "expense"}


# ==================== 2. ДЕКОРАТОРИ ТА ВАЛІДАЦІЯ ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return flask.jsonify({"status": "error", "message": "Unauthorized"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    
    return decorated_function


def parse_and_validate_transaction(data, current_user_id):
    if not data:
        flask.abort(400, description="Data is required")

    # Сума
    try:
        amount = float(data.get("amount"))
        if amount <= 0:
            flask.abort(400, description="Amount must be greater than 0")
    except (ValueError, TypeError):
        flask.abort(400, description="Invalid amount")

    # Тип
    transaction_type = data.get("type")
    if transaction_type not in ALLOWED_TYPES:
        flask.abort(400, description="Invalid transaction type")

    # Дата
    date = data.get("date")
    if not date:
        flask.abort(400, description="Date is required")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        flask.abort(400, description="Invalid date format. Expected YYYY-MM-DD")

    # Категорія (перевіряємо через базу даних)
    category = data.get("category")
    if not category:
        flask.abort(400, description="Category is required")

    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM categories WHERE user_id = %s AND name = %s;",
            (current_user_id, category)
        )
        cursor_exists = cursor.fetchone()
    finally:
        connection.close()

    if not cursor_exists:
        flask.abort(400, description="Invalid category")

    # Опис
    description = data.get("description", "")

    return amount, transaction_type, date, category, description


def get_transaction_data(data):
    return (
        data.get("amount"),
        data.get("type"),
        data.get("date"),
        data.get("category"),
        data.get("description"),
    )


# ==================== 3. ОБРОБНИКИ ПОМИЛОК ====================

@app.errorhandler(400)
def handle_bad_request(error):
    return flask.jsonify({"status": "error", "message": error.description}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return flask.jsonify({"status": "error", "message": "Resource not found"}), 404


@app.errorhandler(500)
def handle_server_error(error):
    return flask.jsonify({"status": "error", "message": "Internal server error"}), 500


# ==================== 4. МАРШРУТИ АВТОРИЗАЦІЇ (AUTH) ====================

@app.route("/login", methods=["GET", "POST"])
def login():  
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        connection = get_db_connection()
        try: 
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user = cursor.fetchone()
        finally:
            connection.close()
        
        if user is None or not check_password_hash(user["password_hash"], password):
           flask.abort(400, description="Invalid username or password")

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register(): 
    if request.method == "POST":
        username = request.form.get('username')
        password_hash = generate_password_hash(request.form.get('password'))

        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id;",
                (username, password_hash)
            )

            user_id = cursor.fetchone()[0]

            default_categories = [
                ('salary', 'income'),
                ('freelance', 'income'),
                ('gifts', 'income'),
                ('groceries', 'expense'),
                ('housing', 'expense'),
                ('transport', 'expense'),
                ('restaurants', 'expense'),
                ('entertainment', 'expense'),
                ('other', 'expense')
            ]

            for name, cat_type in default_categories:
                cursor.execute(
                    "INSERT INTO categories (user_id, name, type) VALUES (%s, %s, %s);",
                    (user_id, name, cat_type)
                )

            connection.commit()
        except psycopg2.errors.UniqueViolation:
            connection.rollback()
            flask.abort(400, description="Username already taken")
        finally:
            connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== 5. WEB-МАРШРУТИ (SSR / HTML) ====================

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/add-transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    current_user_id = session["user_id"]

    connection = get_db_connection()
    try: 
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if request.method == "POST":
            amount, transaction_type, date, category, description = parse_and_validate_transaction(request.form, current_user_id)
            cursor.execute(
                """
                INSERT INTO transactions (amount, type, date, category, description, user_id)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (amount, transaction_type, date, category, description, current_user_id),
            )
            connection.commit()
            return flask.redirect("/")

        cursor.execute("SELECT * FROM categories WHERE user_id = %s ORDER BY type, name;", (current_user_id,))
        categories = cursor.fetchall() 
    finally:
        connection.close()

    return flask.render_template("add_transaction.html", categories=categories)


@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    current_user_id = session["user_id"]

    if request.method == "POST":
        amount, transaction_type, date, category, description = parse_and_validate_transaction(request.form, current_user_id)

        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """ 
                UPDATE transactions
                SET amount = %s, type = %s, date = %s, category = %s, description = %s
                WHERE id = %s AND user_id = %s;
                """,
                (amount, transaction_type, date, category, description, transaction_id, current_user_id),
            )
            if cursor.rowcount == 0:
                flask.abort(404)
            connection.commit()
        finally:
            connection.close()

        return flask.redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE id = %s AND user_id = %s;",
            (transaction_id, current_user_id)
        )
        transaction = cursor.fetchone()

        if transaction is None:
            flask.abort(404)

        cursor.execute(
            "SELECT * FROM categories WHERE user_id = %s ORDER BY type, name;",
            (current_user_id,)
        )
        categories = cursor.fetchall()
    finally:
        connection.close()

    return flask.render_template("edit_transaction.html", transaction=transaction, categories=categories)


@app.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    current_user_id = session["user_id"]

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s;", (transaction_id, current_user_id))
        if cursor.rowcount == 0:
            flask.abort(404)
        connection.commit()
    except psycopg2.Error:
        connection.rollback()
        flask.abort(500)
    finally:
        connection.close()

    return flask.redirect("/")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    current_user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("name")
        category_type = request.form.get("type")

        connection = get_db_connection()
        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (%s, %s, %s);",
                (current_user_id, name, category_type)
            )
            connection.commit()
        finally:
            connection.close()
        return redirect(url_for("settings"))

    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM categories WHERE user_id = %s ORDER BY type, name;", (current_user_id,))
        categories = cursor.fetchall()
    finally:
        connection.close()

    return render_template("settings.html", categories=categories)


@app.route("/category/edit/<int:category_id>", methods=["POST"])
@login_required
def edit_category(category_id):
    current_user_id = session["user_id"]
    name = request.form.get("name")
    category_type = request.form.get("type")

    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "UPDATE categories SET name = %s, type = %s WHERE id = %s AND user_id = %s;",
            (name, category_type, category_id, current_user_id)
        )
        connection.commit()
    finally:
        connection.close()
    return redirect(url_for("settings"))


@app.route("/category/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    current_user_id = session["user_id"]

    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "DELETE FROM categories WHERE id = %s AND user_id = %s;",
            (category_id, current_user_id)
        )
        connection.commit()
    finally: 
        connection.close()
    return redirect(url_for("settings"))

@app.route("/settings/change-password", methods=["POST"])
@login_required
def change_password():
    current_user_id = session["user_id"]
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")

    connection = get_db_connection()

    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
                        SELECT * FROM users WHERE id = %s
                        """, (current_user_id,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password_hash"], old_password):
            flask.abort(400, description="Incorrect old password")

        new_password_hash = generate_password_hash(new_password)

        cursor.execute("""
                        UPDATE users SET password_hash = %s WHERE id = %s
                        """, (new_password_hash, current_user_id))
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for("settings"))


# ==================== 6. REST API МАРШРУТИ ====================

@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    current_user_id = session["user_id"]
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s;", (current_user_id,))
        transactions = cursor.fetchall()
    finally:
        connection.close()

    for transaction in transactions:
        transaction["date"] = transaction["date"].isoformat()
        
    return flask.jsonify(transactions)


@app.route("/api/transactions", methods=["POST"])
@login_required
def create_transaction():
    data = request.get_json()
    current_user_id = session["user_id"]
    amount, transaction_type, date, category, description = parse_and_validate_transaction(data, current_user_id)
    
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            INSERT INTO transactions (amount, type, date, category, description, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (amount, transaction_type, date, category, description, current_user_id),
        )
        transaction_id = cursor.fetchone()["id"]
        connection.commit()
    finally:
        connection.close()

    return flask.jsonify({"id": transaction_id}), 201


@app.route("/api/transactions/<int:transaction_id>", methods=["GET"])
@login_required
def get_transaction(transaction_id):
    current_user_id = session["user_id"]
    connection = get_db_connection()
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM transactions WHERE id = %s AND user_id = %s;",
            (transaction_id, current_user_id)
        )
        transaction = cursor.fetchone()
        if transaction is None:
            flask.abort(404)
    finally:
        connection.close()

    return flask.jsonify(transaction)


@app.route("/api/transactions/<int:transaction_id>", methods=["PUT"])
@login_required
def update_transaction(transaction_id):
    data = request.get_json()
    current_user_id = session["user_id"]
    amount, transaction_type, date, category, description = parse_and_validate_transaction(data, current_user_id)

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """ 
            UPDATE transactions
            SET amount = %s, type = %s, date = %s, category = %s, description = %s
            WHERE id = %s AND user_id = %s;
            """,
            (amount, transaction_type, date, category, description, transaction_id, current_user_id),
        )
        rows_updated = cursor.rowcount
        connection.commit()
    except psycopg2.Error:
        connection.rollback()
        flask.abort(500)
    finally:
        connection.close()

    if rows_updated == 0:
        flask.abort(404)

    return flask.jsonify({"id": transaction_id}), 200


@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction_api(transaction_id):
    current_user_id = session["user_id"]
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE id = %s AND user_id = %s;",
            (transaction_id, current_user_id)
        )
        row_deleted = cursor.rowcount
        connection.commit()
    except psycopg2.Error:
        connection.rollback()
        flask.abort(500)
    finally:
        connection.close()

    if row_deleted == 0:
        flask.abort(404)

    return flask.jsonify({"id": transaction_id}), 200

@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    current_user_id = session["user_id"]
    connection = get_db_connection()

    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(""" 
                        SELECT id, name, type FROM categories WHERE user_id = %s ORDER BY type, name;
                        """, (current_user_id,))
        categories = cursor.fetchall()
    finally:
        connection.close()

    return flask.jsonify(categories)

# ==================== 7. ЗАПУСК СЕРВЕРА ====================

if __name__ == "__main__":
    app.run(debug=True)