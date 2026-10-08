import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
import database
import analytics_engine

app = Flask(__name__)
app.secret_key = "smart-hostel-secret-key-2026"

# Ensure database is initialized at start
database.init_db()


@app.context_processor
def inject_global_data():
    """Injects current date and categories across all templates."""
    now = datetime.now()
    return {
        "current_date_str": now.strftime("%A, %B %d, %Y"),
        "current_year": now.year,
        "app_title": "SmartHostel Complaint Management & Analytics",
        "categories_list": database.CATEGORIES,
        "blocks_list": database.BLOCKS,
        "severities_list": database.SEVERITIES,
        "statuses_list": database.STATUSES
    }


# ==========================================
# DASHBOARD HOME
# ==========================================
@app.route("/")
def dashboard():
    kpis = database.get_kpi_summary()
    
    # Generate Chart JSONs
    trend_chart_json = analytics_engine.get_trend_chart_json(days=30)
    category_chart_json = analytics_engine.get_category_chart_json()
    status_donut_json = analytics_engine.get_status_donut_json()
    block_chart_json, block_insight = analytics_engine.get_block_chart_json()
    severity_chart_json, critical_active = analytics_engine.get_severity_chart_json()
    resolution_chart_json, resolution_insight = analytics_engine.get_resolution_time_chart_json()
    
    # Recent complaints for dashboard preview table
    recent_complaints = database.get_all_complaints(limit=8)

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        kpis=kpis,
        trend_chart_json=trend_chart_json,
        category_chart_json=category_chart_json,
        status_donut_json=status_donut_json,
        block_chart_json=block_chart_json,
        block_insight=block_insight,
        severity_chart_json=severity_chart_json,
        critical_active=critical_active,
        resolution_chart_json=resolution_chart_json,
        resolution_insight=resolution_insight,
        recent_complaints=recent_complaints
    )


# ==========================================
# API FOR DYNAMIC TRENDS TIMEFRAME
# ==========================================
@app.route("/api/trends")
def api_trends():
    days = request.args.get("days", 30, type=int)
    chart_json = analytics_engine.get_trend_chart_json(days=days)
    return jsonify({"success": True, "chart": chart_json})


# ==========================================
# COMPLAINTS MANAGEMENT PAGE
# ==========================================
@app.route("/complaints")
def complaints():
    search = request.args.get("search", "")
    category = request.args.get("category", "All")
    block = request.args.get("block", "All")
    severity = request.args.get("severity", "All")
    status = request.args.get("status", "All")
    sort_by = request.args.get("sort_by", "date_desc")

    complaints_list = database.get_all_complaints(
        search=search,
        category=category,
        block=block,
        severity=severity,
        status=status,
        sort_by=sort_by
    )

    kpis = database.get_kpi_summary()

    return render_template(
        "complaints.html",
        active_page="complaints",
        complaints=complaints_list,
        total_count=len(complaints_list),
        kpis=kpis,
        filters={
            "search": search,
            "category": category,
            "block": block,
            "severity": severity,
            "status": status,
            "sort_by": sort_by
        }
    )


# ==========================================
# COMPLAINT DETAIL & STATUS UPDATE
# ==========================================
@app.route("/api/complaint/<complaint_id>")
def api_get_complaint(complaint_id):
    complaint = database.get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found"}), 404
    return jsonify({"success": True, "complaint": complaint})


@app.route("/api/complaint/<complaint_id>/update-status", methods=["POST"])
def api_update_complaint_status(complaint_id):
    data = request.get_json() or request.form
    new_status = data.get("status")
    resolution_notes = data.get("resolution_notes")
    assigned_to = data.get("assigned_to")

    if not new_status:
        return jsonify({"success": False, "message": "Status is required"}), 400

    success = database.update_complaint_status(
        complaint_id=complaint_id,
        new_status=new_status,
        resolution_notes=resolution_notes,
        assigned_to=assigned_to
    )

    if success:
        return jsonify({
            "success": True,
            "message": f"Complaint {complaint_id} updated to '{new_status}' successfully."
        })
    return jsonify({"success": False, "message": "Failed to update complaint"}), 400


# ==========================================
# ADD COMPLAINT PAGE
# ==========================================
@app.route("/add-complaint", methods=["GET", "POST"])
def add_complaint():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        student_phone = request.form.get("student_phone", "").strip()
        student_email = request.form.get("student_email", "").strip()
        block = request.form.get("block", "Block A")
        room_number = request.form.get("room_number", "").strip()
        category = request.form.get("category", "Other")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        severity = request.form.get("severity", "Medium")
        custom_date = request.form.get("date")

        if not student_name or not student_id or not room_number or not description:
            flash("Please fill in all required fields (Student Name, ID, Room, and Description).", "danger")
            return render_template("add_complaint.html", active_page="add_complaint", form=request.form)

        created_at = None
        if custom_date:
            try:
                # Add current time if only date provided
                created_at = f"{custom_date} {datetime.now().strftime('%H:%M:%S')}"
            except Exception:
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        complaint_code = database.add_new_complaint({
            "student_name": student_name,
            "student_id": student_id,
            "student_phone": student_phone,
            "student_email": student_email,
            "block": block,
            "room_number": room_number,
            "category": category,
            "title": title or f"{category} Issue in {room_number}",
            "description": description,
            "severity": severity,
            "created_at": created_at
        })

        flash(f"Complaint registered successfully with ID #{complaint_code}! Warden team notified.", "success")
        return redirect(url_for("complaints", search=complaint_code))

    return render_template("add_complaint.html", active_page="add_complaint", today_date=datetime.now().strftime("%Y-%m-%d"))


# ==========================================
# ADVANCED ANALYTICS PAGE
# ==========================================
@app.route("/analytics")
def analytics():
    kpis = database.get_kpi_summary()
    
    # Heatmap matrix
    heatmap_json = analytics_engine.get_heatmap_matrix_json()
    
    # Severity vs Resolution time
    sev_res_json = analytics_engine.get_severity_vs_resolution_json()
    
    # Category & Resolution time
    cat_chart_json = analytics_engine.get_category_chart_json()
    res_chart_json, res_insight = analytics_engine.get_resolution_time_chart_json()
    status_donut_json = analytics_engine.get_status_donut_json()

    # Smart AI recommendations
    recommendations = analytics_engine.get_smart_recommendations()

    # Recurrence hotspots (rooms with >= 2 complaints)
    df = analytics_engine.load_dataframe()
    hotspots = []
    if not df.empty:
        room_counts = df.groupby(["block", "room_number"]).size().reset_index(name="count")
        top_rooms = room_counts.sort_values(by="count", ascending=False).head(8)
        hotspots = top_rooms.to_dict(orient="records")

    return render_template(
        "analytics.html",
        active_page="analytics",
        kpis=kpis,
        heatmap_json=heatmap_json,
        sev_res_json=sev_res_json,
        cat_chart_json=cat_chart_json,
        res_chart_json=res_chart_json,
        res_insight=res_insight,
        status_donut_json=status_donut_json,
        recommendations=recommendations,
        hotspots=hotspots
    )


# ==========================================
# HOSTEL BLOCKS OVERVIEW PAGE
# ==========================================
@app.route("/blocks")
def blocks():
    block_summaries = analytics_engine.get_block_health_summary()
    block_chart_json, block_insight = analytics_engine.get_block_chart_json()
    
    return render_template(
        "blocks.html",
        active_page="blocks",
        blocks=block_summaries,
        block_chart_json=block_chart_json,
        block_insight=block_insight
    )


# ==========================================
# REPORTS & EXPORT PAGE
# ==========================================
@app.route("/reports")
def reports():
    kpis = database.get_kpi_summary()
    df = analytics_engine.load_dataframe()

    cat_breakdown = []
    block_breakdown = []
    
    if not df.empty:
        # Category stats
        cat_grouped = df.groupby("category").agg(
            total=("id", "count"),
            resolved=("status", lambda s: (s == "Resolved").sum()),
            pending=("status", lambda s: (s == "Pending").sum()),
            avg_days=("resolution_time_days", "mean")
        ).reset_index()
        cat_grouped["avg_days"] = cat_grouped["avg_days"].round(1).fillna(0)
        cat_breakdown = cat_grouped.sort_values(by="total", ascending=False).to_dict(orient="records")

        # Block stats
        block_grouped = df.groupby("block").agg(
            total=("id", "count"),
            resolved=("status", lambda s: (s == "Resolved").sum()),
            pending=("status", lambda s: (s == "Pending").sum()),
            critical=("severity", lambda s: (s == "Critical").sum())
        ).reset_index()
        block_breakdown = block_grouped.sort_values(by="total", ascending=False).to_dict(orient="records")

    return render_template(
        "reports.html",
        active_page="reports",
        kpis=kpis,
        cat_breakdown=cat_breakdown,
        block_breakdown=block_breakdown
    )


# ==========================================
# CSV EXPORT ENDPOINT
# ==========================================
@app.route("/api/export-csv")
def export_csv():
    complaints = database.get_all_complaints()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = [
        "Complaint ID", "Student Name", "Student ID", "Phone", "Email",
        "Block", "Room Number", "Category", "Title", "Description",
        "Severity", "Status", "Created At", "Resolved At", "Resolution Days",
        "Resolution Notes", "Assigned Staff"
    ]
    writer.writerow(headers)
    
    for c in complaints:
        writer.writerow([
            c["complaint_code"], c["student_name"], c["student_id"], c["student_phone"] or "", c["student_email"] or "",
            c["block"], c["room_number"], c["category"], c["title"], c["description"],
            c["severity"], c["status"], c["created_at"], c["resolved_at"] or "", c["resolution_time_days"] or "",
            c["resolution_notes"] or "", c["assigned_to"] or ""
        ])
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=hostel_complaints_export.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response


# ==========================================
# SETTINGS & DATA RESET PAGE
# ==========================================
@app.route("/settings")
def settings():
    kpis = database.get_kpi_summary()
    return render_template("settings.html", active_page="settings", kpis=kpis)


@app.route("/api/reseed", methods=["POST"])
def reseed_database():
    database.init_db(force_reseed=True)
    flash("Database reset and repopulated with 248 fresh demo complaints!", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    print("\n=======================================================")
    print(" Smart Hostel Complaint Management & Analytics System")
    print(" Local server starting at: http://127.0.0.1:5000")
    print("=======================================================\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
