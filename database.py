
import sqlite3
from datetime import date

DB_NAME = "expenses.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0)
            )
        """)


def add_expense(expense_date, description, category, amount):
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO expenses (date, description, category, amount)
            VALUES (?, ?, ?, ?)
        """, (
            str(expense_date),
            description.strip(),
            category,
            float(amount)
        ))


def get_expenses(start_date=None, end_date=None):
    query = """
        SELECT id, date, description, category, amount
        FROM expenses
    """
    parameters = []
    conditions = []

    if start_date:
        conditions.append("date >= ?")
        parameters.append(str(start_date))

    if end_date:
        conditions.append("date <= ?")
        parameters.append(str(end_date))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY date DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def delete_expense(expense_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (int(expense_id),)
        )


initialize_database()
