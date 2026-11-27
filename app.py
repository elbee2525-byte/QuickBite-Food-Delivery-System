import os
import sqlite3
import json
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

    columns = [row[1] for row in conn.execute("PRAGMA table_info(orders)")]

    if "status" not in columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN status TEXT DEFAULT 'Pending'
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
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

        print("PASSWORD LENGTH:", len(admin_password) if admin_password else 0)
        print("ENTERED LENGTH:", len(request.form.get("password", "")))
        print("PASSWORD MATCH:", request.form.get("password") == admin_password)

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

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()

    order_items_by_id = {}

    for order in orders:
        order_id = order[0]

        cursor.execute("""
            SELECT food_name, quantity, unit_price, line_total
            FROM order_items
            WHERE order_id = ?
        """, (order_id,))

        order_items_by_id[order_id] = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        orders=orders,
        order_items_by_id=order_items_by_id
    )
@app.route("/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    status = request.form.get("status")

    if status not in ["Pending", "Preparing", "Delivered"]:
        return "Invalid order status", 400
    

    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))
@app.route("/place_order", methods=["POST"])
def place_order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    try:
        items = json.loads(request.form.get("items", "[]"))

        if not name or not phone or not address or not items:
            return "Please complete your details and add food to your cart."

        conn = sqlite3.connect("foodie.db")
        cursor = conn.cursor()

        total = 0

        for item in items:
            quantity = int(item["quantity"])
            price = float(item["price"])

            if quantity <= 0 or price < 0:
                raise ValueError("Invalid item")

            total += quantity * price

        cursor.execute("""
            INSERT INTO orders (customer_name, phone, address, total)
            VALUES (?, ?, ?, ?)
        """, (name, phone, address, total))

        order_id = cursor.lastrowid

        for item in items:
            food_name = item["name"]
            quantity = int(item["quantity"])
            price = float(item["price"])
            line_total = quantity * price

            cursor.execute("""
                INSERT INTO order_items
                (order_id, food_name, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, food_name, quantity, price, line_total))

        conn.commit()
        conn.close()

        return redirect(url_for("receipt", order_id=order_id))

    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return "Invalid order details. Please try again."








    


@app.route("/receipt/<int:order_id>")
def receipt(order_id):
    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    )
    order = cursor.fetchone()

    if order is None:
        conn.close()
        return "Order not found", 404

    cursor.execute("""
        SELECT food_name, quantity, unit_price, line_total
        FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    items = cursor.fetchall()

    conn.close()

    return render_template(
        "receipt.html",
        order=order,
        items=items
    )
 

create_database()

if __name__ == "__main__":
    app.run(debug=True)