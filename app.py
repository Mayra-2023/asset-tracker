from flask import Flask, render_template, request, redirect, session, url_for, Response
import os
import psycopg2
from datetime import datetime
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "asset_tracker_secret_key_2026"
init_done = False
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

    # Tabela Assets
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

    # Tabela Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
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
   from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html"),
        username=session.get("username"),
        role=session.get("role")
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM users
            WHERE username=%s
            AND password=%s
        """, (username, password))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["username"] = user[1]
            session["role"] = user[3]
            return redirect("/")

        return "Invalid username or password"

    return render_template("login.html")
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

@app.route("/dashboard")
def dashboard():

    conn = get_conn()
    cur = conn.cursor()

    selected_depot = request.args.get("depot", "")
if selected_depot:
    filter_sql = " WHERE depot = %s "
    filter_params = (selected_depot,)
else:
    filter_sql = ""
    filter_params = ()
    cur.execute("""
        SELECT DISTINCT depot
        FROM assets
        WHERE depot IS NOT NULL
        ORDER BY depot
    """)
    depots = [row[0] for row in cur.fetchall()]

       # KPIs
    cur.execute("SELECT COUNT(*) FROM assets")
    total_assets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE LOWER(status)='active'
    """)
    active_assets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE LOWER(status)='undermaintenance'
    """)
    maintenance_assets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE LOWER(status)='missing'
    """)
    missing_assets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE LOWER(status)='to be scrapped'
    """)
    to_be_scrapped_assets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE LOWER(status)='scrapped'
    """)
    scrapped_assets = cur.fetchone()[0]

    # Assets by Depot
    cur.execute("""
        SELECT depot, COUNT(*)
        FROM assets
        GROUP BY depot
        ORDER BY depot
    """)
    depot_data = cur.fetchall()

    depot_labels = [row[0] for row in depot_data]
    depot_values = [row[1] for row in depot_data]

    # Assets by Status
    if selected_depot:
        cur.execute("""
            SELECT status, COUNT(*)
            FROM assets
            WHERE depot = %s
            GROUP BY status
            ORDER BY status
        """, (selected_depot,))
    else:
        cur.execute("""
            SELECT status, COUNT(*)
            FROM assets
            GROUP BY status
            ORDER BY status
        """)

    status_data = cur.fetchall()

    status_labels = [row[0] for row in status_data]
    status_values = [row[1] for row in status_data]

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_assets=total_assets,
        active_assets=active_assets,
        maintenance_assets=maintenance_assets,
        missing_assets=missing_assets,
        to_be_scrapped_assets=to_be_scrapped_assets,
        scrapped_assets=scrapped_assets,
        depot_labels=depot_labels,
        depot_values=depot_values,
        status_labels=status_labels,
        status_values=status_values,
        depots=depots,
        selected_depot=selected_depot
    )

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
# ADMIN PANEL
# =========================
@app.route("/admin")
def admin():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM assets
        ORDER BY capture_date DESC
    """)

    assets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "admin.html",
        assets=assets
    )
    # =========================
# EDIT ASSET
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_asset(id):

    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":

        asset_id = request.form.get("asset_id")
        depot = request.form.get("depot")
        status = request.form.get("status")
        description = request.form.get("description")
        captured_by = request.form.get("captured_by")
        employee_number = request.form.get("employee_number")

        cur.execute("""
            UPDATE assets
            SET
                asset_id=%s,
                depot=%s,
                status=%s,
                description=%s,
                captured_by=%s,
                employee_number=%s
            WHERE id=%s
        """, (
            asset_id,
            depot,
            status,
            description,
            captured_by,
            employee_number,
            id
        ))

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("admin"))

    cur.execute("""
        SELECT *
        FROM assets
        WHERE id=%s
    """, (id,))

    asset = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "edit_asset.html",
        asset=asset
    )


# =========================
# DELETE ASSET
# =========================
@app.route("/delete/<int:id>")
def delete_asset(id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM assets
        WHERE id=%s
    """, (id,))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("admin"))
# =========================
# TEST USERS TABLE
# =========================
@app.route("/test-users")
def test_users():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
    """)

    tables = cur.fetchall()

    cur.close()
    conn.close()

    return str(tables)


@app.route("/create-admins")
def create_admins():

    conn = get_conn()
    cur = conn.cursor()

    admins = [
        ("Luis Jeje", "admin123", "admin"),
        ("Johan Kleinhans", "admin123", "admin"),
        ("Steve Farrel", "admin123", "admin"),
        ("Telcidio Savel", "admin123", "admin")
    ]

    for username, password, role in admins:
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (username, password, role))

    conn.commit()
    cur.close()
    conn.close()

    return "Admins created successfully"


@app.route("/list-users")
def list_users():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, role
        FROM users
        ORDER BY id
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

    return str(users)


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
    init_db()
    app.run(debug=True)
