from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

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
@app.route("/admin")
def admin():
    conn = sqlite3.connect("foodie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    conn.close()

    return render_template("admin.html", orders=orders)

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