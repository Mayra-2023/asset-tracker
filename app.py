from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
import base64
from datetime import datetime

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = os.path.join(BASE_DIR, "assets.db")

# URL DO SERVIDOR (preencha quando publicar no Render)
RENDER_URL = ""   # Exemplo: "https://seuapp.onrender.com"


# =========================
# BANCO DE DADOS
# =========================

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT,
            depot TEXT,
            status TEXT,
            captured_by TEXT,
            employee_number TEXT,
            image TEXT,
            capture_date TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# HOME
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# ADD ASSET
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_asset():

    if request.method == "POST":

        asset_id = request.form["asset_id"]
        depot = request.form["depot"]
        status = request.form["status"]
        captured_by = request.form["captured_by"]
        employee_number = request.form["employee_number"]

        image = request.files["image"]
        capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{secure_filename(image.filename)}"

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assets (
                asset_id, depot, status, captured_by, employee_number, image, capture_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_id, depot, status, captured_by, employee_number, filename, capture_date))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_asset.html")


# =========================
# SEARCH
# =========================

@app.route("/search", methods=["GET", "POST"])
def search():

    asset = None
    update_required = False

    if request.method == "POST":
        asset_id = request.form["asset_id"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM assets
            WHERE asset_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        asset = cursor.fetchone()
        conn.close()

        if asset:
            capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
            days_difference = (datetime.now() - capture_date).days

            if days_difference >= 180:
                update_required = True

    return render_template("search.html", asset=asset, update_required=update_required)


# =========================
# UPDATES
# =========================

@app.route("/updates")
def updates():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    conn.close()

    expired_assets = []

    for asset in assets:
        capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
        days_difference = (datetime.now() - capture_date).days

        if days_difference >= 180:
            expired_assets.append(asset)

    return render_template("updates.html", assets=expired_assets)


# =========================
# SUMMARY
# =========================

@app.route("/summary")
def summary():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT depot, asset_id, capture_date FROM assets")
    rows = cursor.fetchall()
    conn.close()

    summary = {}

    for depot, asset_id, capture_date in rows:

        if depot not in summary:
            summary[depot] = {"total": 0, "verificados": 0, "nao_verificados": 0}

        summary[depot]["total"] += 1

        days = (datetime.now() - datetime.strptime(capture_date, "%Y-%m-%d %H:%M:%S")).days

        if days <= 180:
            summary[depot]["verificados"] += 1
        else:
            summary[depot]["nao_verificados"] += 1

    return render_template("summary.html", summary=summary)


# =========================
# EXPORT CSV (LINK + BASE64)
# =========================

@app.route("/export")
def export():

    filename = "assets_export.csv"
    filepath = os.path.join(BASE_DIR, filename)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()
    conn.close()

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Asset ID", "Depot", "Status",
            "Captured By", "Employee No",
            "Image URL (Local Path)",
            "Image Base64",
            "Capture Date"
        ])

        for r in rows:

            # ---------------------------
            # URL LOCAL DA IMAGEM
            # ---------------------------
            if r[6]:
                if RENDER_URL:
                    image_url = f"{RENDER_URL}/static/uploads/{r[6]}"
                else:
                    image_url = f"/static/uploads/{r[6]}"
            else:
                image_url = ""

            # ---------------------------
            # IMAGEM EM BASE64
            # ---------------------------
            if r[6]:
                image_path = os.path.join(UPLOAD_FOLDER, r[6])

                if os.path.exists(image_path):
                    with open(image_path, "rb") as img:
                        b64 = base64.b64encode(img.read()).decode("utf-8")
                    image_b64 = f"data:image/jpeg;base64,{b64}"
                else:
                    image_b64 = ""
            else:
                image_b64 = ""

            writer.writerow([
                r[0], r[1], r[2], r[3], r[4], r[5],
                image_url,
                image_b64,
                r[7]
            ])

    return send_file(filepath, as_attachment=True)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
