from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# =========================
# CLOUDINARY
# =========================

print("===== CLOUDINARY TEST =====")
print("CLOUD NAME:", os.environ.get("CLOUDINARY_CLOUD_NAME"))
print("API KEY:", os.environ.get("CLOUDINARY_API_KEY"))

if os.environ.get("CLOUDINARY_API_SECRET"):
    print("API SECRET OK")
else:
    print("API SECRET MISSING")

print("===========================")

# =========================
# CONFIG
# =========================

DATABASE = "assets.db"

# =========================
# DATABASE
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

        try:

            asset_id = request.form.get("asset_id")
            depot = request.form.get("depot")
            status = request.form.get("status")
            captured_by = request.form.get("captured_by")
            employee_number = request.form.get("employee_number")

            image = request.files.get("image")

            if not image:
                return "No image selected", 400

            capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Upload para Cloudinary
            upload_result = cloudinary.uploader.upload(
                image,
                folder="asset_tracker"
            )

            image_url = upload_result["secure_url"]

            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO assets (
                    asset_id,
                    depot,
                    status,
                    captured_by,
                    employee_number,
                    image,
                    capture_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_id,
                depot,
                status,
                captured_by,
                employee_number,
                image_url,
                capture_date
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("index"))

        except Exception as e:
            print("ERROR ADD ASSET:", str(e))
            return f"Error uploading asset: {str(e)}", 500

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
            SELECT *
            FROM assets
            WHERE asset_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        asset = cursor.fetchone()

        conn.close()

        if asset:

            capture_date = datetime.strptime(
                asset[7],
                "%Y-%m-%d %H:%M:%S"
            )

            days_difference = (
                datetime.now() - capture_date
            ).days

            if days_difference >= 365:
                update_required = True

    return render_template(
        "search.html",
        asset=asset,
        update_required=update_required
    )

# =========================
# UPDATE REQUIRED LIST
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

        capture_date = datetime.strptime(
            asset[7],
            "%Y-%m-%d %H:%M:%S"
        )

        days_difference = (
            datetime.now() - capture_date
        ).days

        if days_difference >= 365:
            expired_assets.append(asset)

    return render_template(
        "updates.html",
        assets=expired_assets
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
