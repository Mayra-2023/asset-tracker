from flask import Flask, render_template, request, redirect, url_for, Response
import os
import psycopg2
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
# POSTGRES CONNECTION
# =========================
def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# =========================
# INIT DB
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id SERIAL PRIMARY KEY,
            asset_id TEXT,
            depot TEXT,
            status TEXT,
            description TEXT,
            captured_by TEXT,
            employee_number TEXT,
            image TEXT,
            capture_date TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
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

        asset_id = request.form.get("asset_id")
        depot = request.form.get("depot")
        status = request.form.get("status")
        description = request.form.get("description")
        captured_by = request.form.get("captured_by")
        employee_number = request.form.get("employee_number")

        image = request.files.get("image")

        upload = cloudinary.uploader.upload(image, folder="asset_tracker")
        image_url = upload["secure_url"]

        capture_date = datetime.now()

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO assets (
                asset_id, depot, status, description,
                captured_by, employee_number,
                image, capture_date
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            asset_id, depot, status, description,
            captured_by, employee_number,
            image_url, capture_date
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_asset.html")

# =========================
# SEARCH
# =========================
@app.route("/search", methods=["GET", "POST"])
def search():

    asset = None
    verification_status = None
    update_required = False

    if request.method == "POST":

        asset_id = request.form.get("asset_id")

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM assets
            WHERE asset_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:

            asset = {
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

            days = (datetime.now() - row[8]).days

            if row[3] == "Missing":
                verification_status = "Missing"
            elif days <= 180:
                verification_status = "Verified"
            else:
                verification_status = "Overdue"
                update_required = True

    return render_template(
        "search.html",
        asset=asset,
        verification_status=verification_status,
        update_required=update_required
    )

# =========================
# UPDATES
# =========================
@app.route("/updates")
def updates():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM assets")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    expired = []

    for r in rows:
        if (datetime.now() - r[8]).days >= 180:
            expired.append(r)

    return render_template("updates.html", assets=expired)

# =========================
# SUMMARY
# =========================
@app.route("/summary")
def summary():

    conn = get_conn()
    cur = conn.cursor()

    # Total Assets
    cur.execute("SELECT COUNT(*) FROM assets")
    total_assets = cur.fetchone()[0]

    # Totais por Status
    cur.execute("""
        SELECT status, COUNT(*)
        FROM assets
        GROUP BY status
    """)
    status_rows = cur.fetchall()

    stats = {
        "Active": 0,
        "Standby": 0,
        "Under Maintenance": 0,
        "Damaged": 0,
        "Missing": 0,
        "Disposed": 0
    }

    for status, count in status_rows:
        if status in stats:
            stats[status] = count

    # Assets por Depot
    cur.execute("""
        SELECT depot, COUNT(*)
        FROM assets
        GROUP BY depot
        ORDER BY depot
    """)
    depot_rows = cur.fetchall()

    # Últimos 10 ativos
    cur.execute("""
        SELECT asset_id,
               depot,
               status,
               captured_by,
               capture_date
        FROM assets
        ORDER BY capture_date DESC
        LIMIT 10
    """)
    recent_assets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "summary.html",
        total_assets=total_assets,
        stats=stats,
        depot_rows=depot_rows,
        recent_assets=recent_assets
    )

# =========================
# EXPORT CSV
# =========================
@app.route("/export")
def export():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM assets")
    rows = cur.fetchall()

    cur.close()
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
