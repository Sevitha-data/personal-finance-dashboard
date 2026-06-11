from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date
from datetime import datetime

app = Flask(__name__)

# Database create
def init_db():
    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()

    cur.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    amount REAL,
    type TEXT,
    date TEXT,
    time TEXT
)
""")

    conn.commit()
    conn.close()

init_db()


@app.route("/")
def home():

    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()

    search = request.args.get("search", "")
    filter_type = request.args.get("filter", "")

    if search and filter_type:
        cur.execute(
            """
            SELECT * FROM expenses
            WHERE title LIKE ?
            AND type = ?
            """,
            ('%' + search + '%', filter_type)
        )

    elif search:
        cur.execute(
            "SELECT * FROM expenses WHERE title LIKE ?",
            ('%' + search + '%',)
        )


    elif filter_type:
        cur.execute(
            "SELECT * FROM expenses WHERE type = ?",
            (filter_type,)
        )

    else:
        cur.execute("SELECT * FROM expenses")

    expenses = cur.fetchall()
    expenses.reverse()
    transaction_count = len(expenses)

    income = sum(
        expense[2]
        for expense in expenses
        if expense[3] == "Income"
    )

    expense_total = sum(
        expense[2]
        for expense in expenses
        if expense[3] == "Expense"
    )

    balance = income - expense_total

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        income=income,
        expense_total=expense_total,
        balance=balance,
        transaction_count=transaction_count
    )

@app.route("/add", methods=["POST"])
def add_expense():

    title = request.form["title"]
    amount = request.form["amount"]
    type = request.form["type"]

    today = date.today().strftime("%d-%m-%Y")
    current_time = datetime.now().strftime("%H:%M")

    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO expenses
        (title, amount, type, date, time)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, amount, type, today, current_time)
    )

    conn.commit()
    conn.close()

    return redirect("/")
@app.route("/edit/<int:id>")
def edit_expense(id):

    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM expenses WHERE id=?",
        (id,)
    )

    expense = cur.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        expense=expense
    )
@app.route("/update/<int:id>", methods=["POST"])
def update_expense(id):

    title = request.form["title"]
    amount = request.form["amount"]
    type = request.form["type"]

    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE expenses
        SET title=?, amount=?, type=?
        WHERE id=?
        """,
        (title, amount, type, id)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)