from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os
import time

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "tfg_db")

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True
    )

def init_db():
    """Crea la tabla de usuarios si no existe en el RDS."""
    try:
        conn = get_connection()
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
        conn.close()
        print("✅ Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar DB: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user, pwd = request.form["username"], request.form["password"]
        conn = get_connection()
        with conn.cursor() as c:
            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, pwd))
        conn.close()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user, pwd = request.form["username"], request.form["password"]
        conn = get_connection()
        with conn.cursor() as c:
            c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, pwd))
            result = c.fetchone()
        conn.close()
        if result:
            return render_template("index.html", user=user)
        error = "Credenciales incorrectas"
    return render_template("login.html", error=error)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

