@app.route("/export")
def export():

    depot = request.args.get("depot", "all")
    filter_type = request.args.get("filter", "all")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    query = """
        SELECT asset_id, depot, status, captured_by, employee_number, image, capture_date
        FROM assets
        WHERE 1=1
    """
    params = []

    # DEPOT FILTER
    if depot != "all":
        query += " AND depot = ?"
        params.append(depot)

    # 180 DAYS FILTER
    if filter_type == "verified":
        query += " AND julianday('now') - julianday(capture_date) <= 180"

    elif filter_type == "unverified":
        query += " AND julianday('now') - julianday(capture_date) > 180"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # ZIP IN MEMORY
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        writer.writerow([
            "Asset ID",
            "Depot",
            "Status",
            "Captured By",
            "Employee No",
            "Image URL",
            "Capture Date"
        ])

        BASE_URL = "http://127.0.0.1:5000"

        for row in rows:
            asset_id, depot_val, status, captured_by, emp_no, image, capture_date = row

            # PATH DA IMAGEM
            image_path = os.path.join("static/uploads", image) if image else ""

            # URL DA IMAGEM
            image_url = f"{BASE_URL}/static/uploads/{image}" if image else ""

            writer.writerow([
                asset_id,
                depot_val,
                status,
                captured_by,
                emp_no,
                image_url,
                capture_date
            ])

            # ADD IMAGE TO ZIP
            if image and os.path.exists(image_path):
                zip_file.write(image_path, f"images/{image}")

        zip_file.writestr("assets.csv", csv_buffer.getvalue())

    zip_buffer.seek(0)

    return Response(
        zip_buffer.getvalue(),
        mimetype="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=export_{depot}_{filter_type}.zip"
        }
    )
