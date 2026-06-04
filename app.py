from flask import Flask, render_template, request, redirect, url_for, Response
import psycopg2
import os
from datetime import datetime
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# =========================
# CLOUDINARY
# =========================
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# =========================
# DATABASE (POSTGRESQL)
# =========================
def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id SERIAL PRIMARY KEY,
            asset_id TEXT,
            depot TEXT,
            status TEXT,
            description TEXT,
            captured_by TEXT,
            employee_number TEXT,
            image TEXT,
            capture_date TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

init_db()

# =========================
# HELPERS
# =========================
def row_to_dict(row):
    if not row:
        return None

    return {
        "id": row[0],
        "asset_id": row[1],
        "depot": row[2],
        "status": row[3],
        "description": row[4],
        "captured_by": row[5],
        "employee_number": row[6],
        "image": row[7],
        "capture_date": row[8],
    }

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
            description = request.form.get("description")
            captured_by = request.form.get("captured_by")
            employee_number = request.form.get("employee_number")

            image = request.files.get("image")

            if not image:
                return "No image selected", 400

            upload = cloudinary.uploader.upload(image, folder="asset_tracker")
            image_url = upload["secure_url"]

            capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO assets (
                    asset_id, depot, status, description,
                    captured_by, employee_number,
                    image, capture_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                asset_id, depot, status, description,
                captured_by, employee_number,
                image_url, capture_date
            ))

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("index"))

        except Exception as e:
            print("ADD ERROR:", str(e))
            return f"Error: {str(e)}", 500

    return render_template("add_asset.html")

# =========================
# SEARCH
# =========================
@app.route("/search", methods=["GET", "POST"])
def search():

    asset = None
    update_required = False
    verification_status = None

    if request.method == "POST":

        asset_id = request.form.get("asset_id")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM assets
            WHERE asset_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            asset = row_to_dict(row)

            try:
                status = asset["status"]
                capture_date = datetime.strptime(
                    asset["capture_date"],
                    "%Y-%m-%d %H:%M:%S"
                )

                days = (datetime.now() - capture_date).days

                if status == "Missing":
                    verification_status = "Missing"
                elif days <= 180:
                    verification_status = "Verified"
                else:
                    verification_status = "Overdue"
                    update_required = True

            except Exception as e:
                print("SEARCH ERROR:", str(e))
                verification_status = "Unknown"

    return render_template(
        "search.html",
        asset=asset,
        update_required=update_required,
        verification_status=verification_status
    )

# =========================
# UPDATES
# =========================
@app.route("/updates")
def updates():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    expired = []

    for r in rows:
        try:
            d = datetime.strptime(r[8], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - d).days >= 180:
                expired.append(r)
        except:
            pass

    return render_template("updates.html", assets=expired)

# =========================
# SUMMARY
# =========================
@app.route("/summary")
def summary():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM assets")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    stats = {
        "Active": 0,
        "Standby": 0,
        "Under Maintenance": 0,
        "Damaged": 0,
        "Missing": 0,
        "Disposed": 0
    }

    for r in rows:
        if r[0] in stats:
            stats[r[0]] += 1

    return render_template("summary.html", stats=stats)

# =========================
# EXPORT CSV
# =========================
@app.route("/export")
def export():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    def generate():
        yield "id,asset_id,depot,status,description,captured_by,employee_number,image,capture_date\n"

        for r in rows:
            yield ",".join([str(x) if x else "" for x in r]) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=assets.csv"}
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
