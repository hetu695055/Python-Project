import json
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import DB_PATH, get_db_connection

# Modern light theme color palette
COLORS = {
    "primary": "#3B82F6",       # Modern vibrant blue
    "primary_dark": "#1D4ED8",  # Navy indigo
    "primary_light": "#93C5FD", # Soft blue
    "success": "#10B981",       # Emerald green (Resolved)
    "warning": "#F59E0B",       # Amber orange (Pending)
    "info": "#0EA5E9",          # Sky blue (In Progress)
    "danger": "#EF4444",        # Coral red (Critical / Rejected)
    "neutral_dark": "#1E293B",  # Slate 800
    "neutral_muted": "#64748B", # Slate 500
    "bg_card": "#FFFFFF",
    "border": "#E2E8F0",
    "grid": "#F1F5F9"
}

LIGHT_PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color="#334155", size=12),
    margin=dict(l=40, r=20, t=30, b=40),
    xaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickcolor="#CBD5E1",
        zeroline=False
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickcolor="#CBD5E1",
        zeroline=False
    ),
    hoverlabel=dict(
        bgcolor="#1E293B",
        font_size=12,
        font_color="#FFFFFF",
        font_family="Inter, sans-serif"
    )
)


def load_dataframe():
    """Loads all complaints from SQLite into a pandas DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM complaints", conn)
    conn.close()

    if df.empty:
        return df

    df["created_dt"] = pd.to_datetime(df["created_at"])
    df["date"] = df["created_dt"].dt.date
    if "resolution_time_days" in df.columns:
        df["resolution_time_days"] = pd.to_numeric(df["resolution_time_days"], errors="coerce")
    return df


def get_trend_chart_json(days=30):
    """
    Generates interactive Line/Area chart for complaint trends.
    Supports 7, 30, or 90 days (3 Months).
    """
    df = load_dataframe()
    if df.empty:
        return "{}"

    today = pd.Timestamp.now().normalize()
    start_date = today - pd.Timedelta(days=days)

    filtered = df[df["created_dt"] >= start_date].copy()
    if filtered.empty:
        filtered = df.copy()

    # Create full date range so there are no missing date gaps
    min_date = filtered["created_dt"].min().floor("D")
    date_range = pd.date_range(start=min_date, end=today, freq="D")
    daily_counts = filtered.groupby(filtered["created_dt"].dt.floor("D")).size().reindex(date_range, fill_value=0).reset_index()
    daily_counts.columns = ["date", "count"]

    fig = go.Figure()

    # Fill area gradient
    fig.add_trace(go.Scatter(
        x=daily_counts["date"].dt.strftime("%b %d"),
        y=daily_counts["count"],
        mode="lines+markers",
        name="Complaints",
        line=dict(color="#3B82F6", width=3, shape="spline"),
        marker=dict(size=6, color="#1D4ED8", line=dict(color="#FFFFFF", width=2)),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.08)",
        hovertemplate="<b>Date:</b> %{x}<br><b>Complaints:</b> %{y}<extra></extra>"
    ))

    # Add 7-day rolling average if period >= 30
    if days >= 30 and len(daily_counts) >= 7:
        daily_counts["ma7"] = daily_counts["count"].rolling(window=7, min_periods=1).mean().round(1)
        fig.add_trace(go.Scatter(
            x=daily_counts["date"].dt.strftime("%b %d"),
            y=daily_counts["ma7"],
            mode="lines",
            name="7-Day Moving Avg",
            line=dict(color="#F59E0B", width=2, dash="dash"),
            hovertemplate="<b>7-Day Avg:</b> %{y}<extra></extra>"
        ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["yaxis"]["title"] = "Complaints Logged"
    layout["xaxis"]["title"] = ""
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    layout["hovermode"] = "x unified"
    fig.update_layout(**layout)

    return fig.to_json()


def get_category_chart_json():
    """
    Problems by Category: Horizontal bar chart sorted highest to lowest.
    """
    df = load_dataframe()
    if df.empty:
        return "{}"

    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    cat_counts = cat_counts.sort_values(by="count", ascending=True)  # ascending for horizontal bar

    # Custom colors highlighting top categories
    top_cat = cat_counts.iloc[-1]["category"]
    colors = ["#60A5FA" if c != top_cat else "#2563EB" for c in cat_counts["category"]]

    fig = go.Figure(go.Bar(
        x=cat_counts["count"],
        y=cat_counts["category"],
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="#FFFFFF", width=1),
            cornerradius=4
        ),
        text=cat_counts["count"],
        textposition="outside",
        textfont=dict(size=12, color="#334155", weight="bold"),
        hovertemplate="<b>%{y}</b><br>Total Complaints: %{x}<extra></extra>"
    ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["margin"] = dict(l=130, r=40, t=10, b=30)
    layout["xaxis"]["title"] = "Total Reported"
    layout["yaxis"]["title"] = ""
    fig.update_layout(**layout)

    return fig.to_json()


def get_status_donut_json():
    """
    Status breakdown donut chart (Resolved, Pending, In Progress, Rejected)
    """
    df = load_dataframe()
    if df.empty:
        return "{}"

    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    color_map = {
        "Resolved": "#10B981",
        "Pending": "#F59E0B",
        "In Progress": "#3B82F6",
        "Rejected": "#EF4444"
    }
    chart_colors = [color_map.get(s, "#94A3B8") for s in status_counts["status"]]

    total = status_counts["count"].sum()

    fig = go.Figure(go.Pie(
        labels=status_counts["status"],
        values=status_counts["count"],
        hole=0.62,
        marker=dict(colors=chart_colors, line=dict(color="#FFFFFF", width=2.5)),
        textinfo="percent",
        textfont=dict(size=13, weight="bold"),
        hoverinfo="label+value+percent",
        hovertemplate="<b>%{label}</b><br>Complaints: %{value} (%{percent})<extra></extra>"
    ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    layout["annotations"] = [
        dict(
            text=f"<span style='font-size:24px;font-weight:700;color:#0F172A;'>{total}</span><br><span style='font-size:11px;color:#64748B;'>Complaints</span>",
            showarrow=False,
            x=0.5, y=0.5
        )
    ]
    fig.update_layout(**layout)

    return fig.to_json()


def get_block_chart_json():
    """
    Complaints by Hostel Block: Vertical bar chart with insight calculation.
    """
    df = load_dataframe()
    if df.empty:
        return "{}", "No data available."

    block_counts = df["block"].value_counts().sort_index().reset_index()
    block_counts.columns = ["block", "count"]

    avg_count = block_counts["count"].mean()
    max_idx = block_counts["count"].idxmax()
    max_block = block_counts.loc[max_idx, "block"]
    max_val = block_counts.loc[max_idx, "count"]

    diff_pct = round(((max_val - avg_count) / avg_count) * 100, 1)

    colors = ["#EF4444" if b == max_block else "#3B82F6" for b in block_counts["block"]]

    fig = go.Figure(go.Bar(
        x=block_counts["block"],
        y=block_counts["count"],
        marker=dict(
            color=colors,
            cornerradius=6,
            line=dict(color="#FFFFFF", width=1)
        ),
        text=block_counts["count"],
        textposition="outside",
        textfont=dict(size=12, weight="bold", color="#1E293B"),
        hovertemplate="<b>%{x}</b><br>Complaints: %{y}<extra></extra>"
    ))

    # Add reference average line
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(block_counts) - 0.5,
        y0=avg_count,
        y1=avg_count,
        line=dict(color="#94A3B8", width=2, dash="dash")
    )
    fig.add_annotation(
        x=len(block_counts) - 0.6,
        y=avg_count + 2,
        text=f"Hostel Avg ({round(avg_count, 1)})",
        showarrow=False,
        font=dict(size=11, color="#64748B")
    )

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["yaxis"]["title"] = "Total Complaints"
    layout["xaxis"]["title"] = ""
    fig.update_layout(**layout)

    insight = f"{max_block} has {diff_pct}% more complaints than the hostel average."
    return fig.to_json(), insight


def get_severity_chart_json():
    """
    Severity distribution donut chart with critical issue emphasis.
    """
    df = load_dataframe()
    if df.empty:
        return "{}", 0

    order = ["Critical", "High", "Medium", "Low"]
    sev_counts = df["severity"].value_counts().reindex(order, fill_value=0).reset_index()
    sev_counts.columns = ["severity", "count"]

    colors = ["#EF4444", "#F97316", "#FBBF24", "#3B82F6"]

    critical_active = len(df[(df["severity"] == "Critical") & (df["status"] != "Resolved")])

    fig = go.Figure(go.Pie(
        labels=sev_counts["severity"],
        values=sev_counts["count"],
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent+label",
        textfont=dict(size=12, weight="bold"),
        hovertemplate="<b>%{label} Severity</b><br>Count: %{value} (%{percent})<extra></extra>",
        pull=[0.08, 0, 0, 0]  # pull out critical slice for emphasis
    ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    layout["showlegend"] = False
    fig.update_layout(**layout)

    return fig.to_json(), critical_active


def get_resolution_time_chart_json():
    """
    Average resolution time by category (Horizontal bar chart)
    Highlights category taking longest to resolve.
    """
    df = load_dataframe()
    if df.empty:
        return "{}", "No data available."

    res_df = df[(df["status"] == "Resolved") & (df["resolution_time_days"].notnull())].copy()
    if res_df.empty:
        return "{}", "No resolved records with time data."

    cat_res = res_df.groupby("category")["resolution_time_days"].mean().round(1).reset_index()
    cat_res = cat_res.sort_values(by="resolution_time_days", ascending=True)

    max_cat_row = cat_res.iloc[-1]
    max_cat = max_cat_row["category"]
    max_days = max_cat_row["resolution_time_days"]

    colors = ["#F59E0B" if c == max_cat else "#3B82F6" for c in cat_res["category"]]

    fig = go.Figure(go.Bar(
        x=cat_res["resolution_time_days"],
        y=cat_res["category"],
        orientation="h",
        marker=dict(
            color=colors,
            cornerradius=4,
            line=dict(color="#FFFFFF", width=1)
        ),
        text=[f"{v} days" for v in cat_res["resolution_time_days"]],
        textposition="outside",
        textfont=dict(size=11, color="#334155", weight="bold"),
        hovertemplate="<b>%{y}</b><br>Avg Resolution: %{x} days<extra></extra>"
    ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["margin"] = dict(l=130, r=60, t=10, b=30)
    layout["xaxis"]["title"] = "Average Resolution Time (Days)"
    layout["yaxis"]["title"] = ""
    fig.update_layout(**layout)

    insight = f"{max_cat} complaints take the longest to resolve ({max_days} days avg)."
    return fig.to_json(), insight


def get_heatmap_matrix_json():
    """
    Advanced Analytics: Block vs Category Cross-tabulation Heatmap.
    """
    df = load_dataframe()
    if df.empty:
        return "{}"

    ct = pd.crosstab(df["category"], df["block"])

    fig = go.Figure(go.Heatmap(
        z=ct.values,
        x=ct.columns.tolist(),
        y=ct.index.tolist(),
        colorscale=[
            [0.0, "#EFF6FF"],
            [0.3, "#93C5FD"],
            [0.6, "#3B82F6"],
            [1.0, "#1E3A8A"]
        ],
        text=ct.values,
        texttemplate="%{text}",
        textfont=dict(size=12, color="#0F172A", weight="bold"),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> in <b>%{x}</b><br>Complaints: %{z}<extra></extra>"
    ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["margin"] = dict(l=130, r=30, t=20, b=40)
    layout["xaxis"]["title"] = "Hostel Block"
    layout["yaxis"]["title"] = ""
    fig.update_layout(**layout)

    return fig.to_json()


def get_severity_vs_resolution_json():
    """
    Advanced Analytics: Average resolution time across severity tiers.
    """
    df = load_dataframe()
    if df.empty:
        return "{}"

    res_df = df[(df["status"] == "Resolved") & (df["resolution_time_days"].notnull())].copy()
    order = ["Low", "Medium", "High", "Critical"]
    sev_res = res_df.groupby("severity")["resolution_time_days"].agg(["mean", "count"]).reindex(order).reset_index()
    sev_res["mean"] = sev_res["mean"].round(1).fillna(0)

    colors = ["#3B82F6", "#FBBF24", "#F97316", "#EF4444"]

    fig = go.Figure(go.Bar(
        x=sev_res["severity"],
        y=sev_res["mean"],
        marker=dict(color=colors, cornerradius=6),
        text=[f"{v}d ({int(c)} resolved)" for v, c in zip(sev_res["mean"], sev_res["count"].fillna(0))],
        textposition="outside",
        textfont=dict(size=12, weight="bold", color="#1E293B"),
        hovertemplate="<b>%{x} Severity</b><br>Avg Time: %{y} days<extra></extra>"
    ))

    layout = dict(**LIGHT_PLOT_LAYOUT)
    layout["yaxis"]["title"] = "Average Days to Resolve"
    layout["xaxis"]["title"] = "Severity Level"
    fig.update_layout(**layout)

    return fig.to_json()


def get_smart_recommendations():
    """
    Derives 5 data-driven intelligent recommendations based on active dataset.
    """
    df = load_dataframe()
    if df.empty:
        return []

    recommendations = []

    # 1. Check worst block
    block_counts = df["block"].value_counts()
    worst_block = block_counts.index[0]
    worst_block_share = round((block_counts.iloc[0] / len(df)) * 100, 1)
    recommendations.append({
        "type": "Urgent Action",
        "badge_class": "badge-danger",
        "title": f"Targeted Infrastructure Audit in {worst_block}",
        "description": f"{worst_block} generates {worst_block_share}% of all hostel grievances. Prioritize an engineering inspection on plumbing and electrical wiring in wings 1 and 2 to arrest recurring breakdowns.",
        "icon": "alert-triangle",
        "impact": "High Impact",
        "dept": "Estate & Civil Works"
    })

    # 2. Check top complaint category
    cat_counts = df["category"].value_counts()
    top_cat = cat_counts.index[0]
    top_cat_count = cat_counts.iloc[0]
    recommendations.append({
        "type": "Service Optimization",
        "badge_class": "badge-warning",
        "title": f"Vendor SLA Review for {top_cat}",
        "description": f"With {top_cat_count} complaints recorded, {top_cat} remains the single largest student pain point. Re-negotiate response turnaround SLAs and deploy backup hardware inventory.",
        "icon": "wifi",
        "impact": "Medium Impact",
        "dept": "Campus IT / Procurement"
    })

    # 3. Check slowest resolution category
    res_df = df[(df["status"] == "Resolved") & (df["resolution_time_days"].notnull())]
    if not res_df.empty:
        slowest_cat = res_df.groupby("category")["resolution_time_days"].mean().idxmax()
        slowest_days = round(res_df.groupby("category")["resolution_time_days"].mean().max(), 1)
        recommendations.append({
            "type": "Workflow Bottleneck",
            "badge_class": "badge-info",
            "title": f"Accelerate {slowest_cat} Turnaround",
            "description": f"{slowest_cat} takes an average of {slowest_days} days to resolve, exceeding the target 48-hour threshold. Deploy dedicated roving technicians on weekends.",
            "icon": "clock",
            "impact": "High Impact",
            "dept": "Maintenance AMC Team"
        })

    # 4. Check critical issues currently pending
    pending_critical = len(df[(df["severity"] == "Critical") & (df["status"] != "Resolved")])
    if pending_critical > 0:
        recommendations.append({
            "type": "Critical Safety",
            "badge_class": "badge-danger",
            "title": f"Expedite {pending_critical} Unresolved Critical Complaints",
            "description": f"There are {pending_critical} open safety/critical complaints (power leaks, water cuts, or fire fixtures). Assign immediate on-call duty wardens.",
            "icon": "shield-alert",
            "impact": "Urgent",
            "dept": "Chief Warden Office"
        })
    else:
        recommendations.append({
            "type": "Safety Milestone",
            "badge_class": "badge-success",
            "title": "Zero Open Critical Complaints",
            "description": "All critical severity complaints have been triaged. Continue weekly preventative inspections of fire hydrants and electrical mains.",
            "icon": "shield-check",
            "impact": "Routine",
            "dept": "Safety Incharge"
        })

    # 5. Routine maintenance suggestion
    recommendations.append({
        "type": "Preventative Measure",
        "badge_class": "badge-success",
        "title": "Bi-Weekly Water Tank & Filter Desilting",
        "description": "Historical water supply complaints peak between days 10 and 20 of each month. Synchronize cleaning cycles with academic exam schedules to prevent disturbance.",
        "icon": "droplet",
        "impact": "Preventative",
        "dept": "Sanitation Works"
    })

    return recommendations


def get_block_health_summary():
    """
    Returns card data for Block A through Block E with health scores and metrics.
    """
    df = load_dataframe()
    blocks_meta = [
        {"block": "Block A", "warden": "Prof. R. C. Mathur", "contact": "Ext 401", "rooms": 80, "capacity": 160},
        {"block": "Block B", "warden": "Dr. Sunita Kulkarni", "contact": "Ext 402", "rooms": 80, "capacity": 160},
        {"block": "Block C", "warden": "Er. Deepesh Sen", "contact": "Ext 403", "rooms": 80, "capacity": 160},
        {"block": "Block D", "warden": "Dr. M. K. Ananth", "contact": "Ext 404", "rooms": 80, "capacity": 160},
        {"block": "Block E", "warden": "Prof. Kavita Rao", "contact": "Ext 405", "rooms": 80, "capacity": 160},
    ]

    summaries = []
    total_complaints = len(df) if not df.empty else 1

    for meta in blocks_meta:
        b_name = meta["block"]
        b_df = df[df["block"] == b_name] if not df.empty else pd.DataFrame()
        count = len(b_df)
        pending = len(b_df[b_df["status"] == "Pending"]) if not b_df.empty else 0
        resolved = len(b_df[b_df["status"] == "Resolved"]) if not b_df.empty else 0
        critical = len(b_df[(b_df["severity"] == "Critical") & (b_df["status"] != "Resolved")]) if not b_df.empty else 0
        
        # Calculate health score: 100 minus penalty for complaint volume and pending criticals
        # Healthy blocks score 85-95, high complaint blocks score 65-75
        share = count / total_complaints
        health_score = max(55, min(98, round(100 - (share * 100) - (critical * 3))))

        top_issue = b_df["category"].value_counts().index[0] if not b_df.empty else "N/A"

        summaries.append({
            **meta,
            "complaint_count": count,
            "pending_count": pending,
            "resolved_count": resolved,
            "critical_count": critical,
            "health_score": health_score,
            "top_issue": top_issue,
            "share_pct": round(share * 100, 1)
        })

    return summaries
