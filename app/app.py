from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

from werkzeug.middleware.proxy_fix import ProxyFix

""" Decallracion para que Flask confie en las cabeceras del ALB (HTTPS)"""
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

""" Clave necesaria para manejar sesiones y mensajes flash en Flask"""
app.secret_key = os.getenv("SECRET_KEY", "tfg_focas_secret_key_2026")

""" Configuración RDS desde variables de entorno"""
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "tfg_db")

def get_connection():
    """Establece conexión con el RDS con autocommit activo."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True
    )

def init_db():
    """Inicializa la tabla de usuarios si no existe."""
    try:
        conn = get_connection()
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            """)
        conn.close()
        print(" Base de datos verificada correctamente.")
    except Exception as e:
        print(f" Error crítico inicializando DB: {e}")

@app.route("/health")
def health():
    """Ruta simple para que el balanceador de carga verifique que la instancia está viva."""
    return "OK", 200

@app.route("/")
def home():
    """ Recogemos el usuario de los parámetros si acaba de hacer login"""
    user = request.args.get('user')
    return render_template("index.html", user=user)

@app.route("/habits")
def habitos():
    return render_template("habits.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")
        if not user or not pwd:
            return render_template("register.html", error="Usuario y contraseña obligatorios")

        # Hash con pbkdf2:sha256 + salt aleatorio (werkzeug por defecto)
        pwd_hash = generate_password_hash(pwd)

        try:
            conn = get_connection()
            with conn.cursor() as c:
                c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, pwd_hash))
            conn.close()
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError:
            return render_template("register.html", error="El usuario ya existe")
        except Exception as e:
            return render_template("register.html", error="Error de conexión")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")
        try:
            conn = get_connection()
            with conn.cursor() as c:
                # Solo seleccionamos el hash; la verificación se hace en Python
                c.execute("SELECT password FROM users WHERE username=%s", (user,))
                result = c.fetchone()
            conn.close()
        except Exception:
            return render_template("login.html", error="Error de conexión")

        # check_password_hash hace la comparación en tiempo constante
        if result and check_password_hash(result[0], pwd):
            session['user'] = user
            return redirect(url_for('home'))

        error = "Credenciales incorrectas"
    return render_template("login.html", error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('home'))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
