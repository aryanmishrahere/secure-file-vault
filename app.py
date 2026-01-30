from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os, sqlite3, io

from crypto_utils import encrypt_file, decrypt_file
from database import DB_PATH

app = Flask(__name__)
app.secret_key = "super-secret-key"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def log_action(username, action):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs VALUES (NULL, ?, ?)", (username, action))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", (u,))
        row = cur.fetchone()
        conn.close()

        if row and check_password_hash(row[0], p):
            session["user"] = u
            log_action(u, "Logged in")
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u, p))
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    files = os.listdir(UPLOAD_FOLDER)

    if request.method == "POST":
        file = request.files["file"]
        encrypted = encrypt_file(file.read())

        with open(os.path.join(UPLOAD_FOLDER, file.filename), "wb") as f:
            f.write(encrypted)

        log_action(session["user"], f"Uploaded {file.filename}")

    return render_template("dashboard.html", files=files)

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "rb") as f:
        decrypted = decrypt_file(f.read())

    log_action(session["user"], f"Downloaded {filename}")
    return send_file(io.BytesIO(decrypted), download_name=filename, as_attachment=True)

app.run(debug=True)
