# =========================
# EXPORT CSV COM LINK DA IMAGEM
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
            "ID",
            "Asset ID",
            "Depot",
            "Status",
            "Verification Status",
            "Captured By",
            "Employee Number",
            "Image URL",
            "Capture Date"
        ])

        for row in rows:

            status = row[3]
            image = row[6]

            # Se estiveres a guardar apenas o nome do ficheiro
            if image.startswith("http"):
                image_url = image
            else:
                image_url = request.host_url.rstrip("/") + "/static/uploads/" + image

            capture_date = datetime.strptime(
                row[7],
                "%Y-%m-%d %H:%M:%S"
            )

            days = (datetime.now() - capture_date).days

            # Estado de verificação
            if status == "Missing":
                verification_status = "Missing"

            elif days <= 180:
                verification_status = "Verified"

            else:
                verification_status = "Overdue"

            writer.writerow([
                row[0],                 # ID
                row[1],                 # Asset ID
                row[2],                 # Depot
                row[3],                 # Status
                verification_status,    # Verification Status
                row[4],                 # Captured By
                row[5],                 # Employee Number
                image_url,              # Link da imagem
                row[7]                  # Capture Date
            ])

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )
