from flask import Flask, request
import pymysql
import os

app = Flask(__name__)

# Variables de entorno 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "tfg_db")

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

# Crear tabla si no existe
def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255),
            password VARCHAR(255)
        )
    """)
    conn.commit()
    conn.close()

# Página principal
@app.route("/")
def home():
    return """
    <h1>🦭 Web de focas</h1>
    <a href='/register'>Registro</a><br>
    <a href='/login'>Login</a>
    """

# Registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (%s, %s)", (user, pwd))
        conn.commit()
        conn.close()

        return "Usuario registrado 🦭"

    return '''
    <form method="post">
        Usuario: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit">
    </form>
    '''

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, pwd))
        result = c.fetchone()
        conn.close()

        if result:
            return f"Bienvenido {user} 🦭"
        else:
            return "Login incorrecto"

    return '''
    <form method="post">
        Usuario: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit">
    </form>
    '''

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
