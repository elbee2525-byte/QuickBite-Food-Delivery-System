import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temporary-development-key")
# Create database
def create_database():
    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            address TEXT,
            total REAL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        admin_password = os.environ.get("ADMIN_PASSWORD")

        if not admin_password:
            error = "Admin password is not configured."
        elif request.form.get("password") == admin_password:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Incorrect password!"

    return render_template("login.html", error=error)


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    conn.close()

    return render_template("admin.html", orders=orders)
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    conn.close()

    return render_template("admin.html", orders=orders)

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))
@app.route("/place_order", methods=["POST"])
def place_order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")
    total = request.form.get("total")

    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (customer_name, phone, address, total)
        VALUES (?, ?, ?, ?)
    """, (name, phone, address, total))

    conn.commit()
    conn.close()

    return "Your order has been placed successfully!"


create_database()

if __name__ == "__main__":
    app.run(debug=True)