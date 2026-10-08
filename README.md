# Smart Hostel Complaint Management & Analytics System

A full-featured, modern, and responsive Python web application designed for hostel facility administration, grievance tracking, and data-driven maintenance analytics. Built as a college mini project that mirrors an enterprise SaaS analytics product.

![Theme](https://img.shields.io/badge/Theme-Modern%20Light-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-brightgreen.svg)
![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)
![Database](https://img.shields.io/badge/Database-SQLite%203-blue.svg)
![Analytics](https://img.shields.io/badge/Analytics-Pandas%20%26%20NumPy-orange.svg)
![Visualization](https://img.shields.io/badge/Charts-Plotly-purple.svg)

---

## 🌟 Key Highlights

* **100% Self-Contained:** Zero dependence on Kaggle, external CSV files, or third-party APIs. The application automatically initializes its own SQLite database with realistic synthetic complaint records upon first launch.
* **Modern Light Theme SaaS UI:** Clean white surfaces, soft shadows, subtle borders, 8px grid system, and semantic color accents (Emerald for Resolved, Amber for Pending, Coral Red for Critical).
* **Interactive Data Visualizations:** High-performance Plotly charts with responsive tooltips, range selectors, and moving averages.
* **Complete Complaint Lifecycle:** Pending ➔ In Progress ➔ Resolved / Rejected workflow with staff assignment and resolution timestamp logging.
* **Smart Analytics & Recommendations:** Automated statistical insights identifying problematic blocks (e.g. *Block B has 32% more complaints than average*), category turnaround bottlenecks, and cross-tabulation heatmaps.

---

## 📁 Project Architecture

```
Python Project/
├── app.py                     # Flask web server, route controllers & REST API endpoints
├── database.py                # SQLite schema, connection utilities & realistic seed generator
├── analytics_engine.py        # Pandas/NumPy analytics calculations & Plotly chart generators
├── requirements.txt           # Python dependencies (Flask, pandas, numpy, plotly, etc.)
├── README.md                  # Comprehensive project documentation
├── static/
│   ├── css/
│   │   └── style.css          # Modern Light Theme design system (SaaS dashboard aesthetic)
│   └── js/
│       ├── main.js            # Sidebar toggle, date helpers, alerts, toast notifications
│       ├── dashboard.js       # Dynamic Plotly rendering & 7d/30d/90d range switcher
│       └── complaints.js      # Modal inspector, filtering & status workflow updates
└── templates/
    ├── base.html              # Core app shell with sidebar navigation, header, & modals
    ├── dashboard.html         # Executive overview dashboard with 4 KPIs and 6 charts
    ├── complaints.html        # Comprehensive complaints registry with search & filters
    ├── add_complaint.html     # Complaint submission form with client validation
    ├── analytics.html         # Dedicated advanced analytics, heatmap & recommendations
    ├── blocks.html            # Hostel Blocks health scorecard (Block A - E)
    ├── reports.html           # Audit report, SLA compliance tables & CSV export
    └── settings.html          # System preferences, SLA benchmarks & database reseed tool
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure **Python 3.10+** (Python 3.11 recommended) is installed on your system.

### 2. Install Dependencies
Open your terminal or command prompt in the project root directory and run:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Flask development server:

```bash
python app.py
```

### 4. Open in Browser
Visit the following URL in your web browser:
```
http://127.0.0.1:5000
```

---

## 📊 Dashboard & System Features

### 1. Executive Dashboard (`/`)
* **Top KPI Metrics:**
  * **Total Complaints:** 248 (+12.5% monthly change indicator)
  * **Pending Complaints:** 42 (17% of total volume)
  * **Resolved Complaints:** 184 (74.2% resolution rate)
  * **Critical Issues:** 12 total logged (with real-time active triage warnings)
* **Complaint Trends:** Interactive Line/Area chart displaying daily logs over **7 Days**, **30 Days**, or **3 Months** with a 7-day rolling moving average.
* **Problems by Category:** Sorted horizontal bar chart covering all 10 hostel domains (Mess, Wi-Fi, Electricity, Water Supply, Cleaning, Bathroom, Furniture, Maintenance, Security, Other).
* **Complaint Status Donut:** Distribution of Resolved, Pending, In Progress, and Rejected tickets with percentage readouts.
* **Hostel Block Analysis:** Vertical bar chart comparing Block A through Block E with an automated benchmark indicator (*Block B has 32% more complaints than average*).
* **Severity Distribution:** Urgency stratification with emphasized critical alerts.
* **Resolution Turnaround:** Average days to turnaround by category, highlighting slowest service sectors (*Maintenance takes the longest to resolve at 3.1 days*).
* **Recent Complaints Table:** Live preview of latest tickets with immediate modal inspection.

### 2. Complaints Management (`/complaints`)
* Full-text search across Complaint Code, Student Name, Roll Number, Room Number, and Problem Description.
* Multi-criteria filters by Category, Block, Severity, and Status.
* Sorting by Newest First, Oldest First, Highest Priority First, or Status Grouping.
* **Interactive Status Modal:** Allows administrators to advance status (Pending ➔ In Progress ➔ Resolved), log resolution notes, and assign personnel.

### 3. Add Complaint Form (`/add-complaint`)
* Student identification (Name, Roll Number, Phone, Email).
* Block and Room selection.
* Category & Severity classification (Low, Medium, High, Critical).
* Automatic ticket code generation (e.g. `#C1249`).
* Real-time dashboard and database synchronization.

### 4. Advanced Analytics (`/analytics`)
* **Data-Driven Recommendation Engine:** 5 actionable administrative directives derived through Pandas aggregations.
* **Block vs Category Heatmap Matrix:** Two-dimensional density distribution revealing problem epicenters.
* **Turnaround Speed by Severity Tier:** Turnaround comparison between Low, Medium, High, and Critical issues.
* **Recurrent Complaint Hotspots:** Detects rooms with repeated maintenance requests.

### 5. Hostel Blocks View (`/blocks`)
* Health scorecards for **Block A**, **Block B**, **Block C**, **Block D**, and **Block E**.
* Displays Warden-in-charge, room count, active critical issues, top grievance categories, and a 0–100 Block Health Score.

### 6. Reports & Data Export (`/reports` & `/api/export-csv`)
* Printable executive audit summary via standard browser print dialog.
* Instant CSV download (`hostel_complaints_export.csv`) containing complete records with timestamps and resolution notes.

### 7. Settings & Reset (`/settings`)
* View database engine health and active record counts.
* **Reseed Database Button:** Instantly repopulates 248 fresh demo complaints matching exact statistical distributions.

---

## 🛠 Technology Stack

| Layer | Component | Version / Library |
|---|---|---|
| **Backend** | Python & Flask | Python 3.11, Flask 3.1 |
| **Database** | SQLite 3 | Built-in zero-config local storage |
| **Data Processing** | Pandas & NumPy | Pandas 3.0, NumPy 2.4 |
| **Visualization** | Plotly | Plotly 7.1 & Plotly.js |
| **Frontend** | HTML5, Vanilla CSS, JS | Modern Light Theme Design System |
| **Typography** | Inter Font | Google Fonts |

---

## 🎓 College Viva / Project Evaluation Talking Points

1. **Why SQLite instead of external CSVs or Kaggle?**
   * Eliminates broken file paths and external API rate limits.
   * Enables true transactional consistency (CRUD operations) where newly added complaints immediately persist and recalculate all charts.
2. **How is the dataset generated?**
   * Uses realistic synthetic modeling with Gaussian distribution for turnaround durations, realistic student rosters, room allocations, and domain-specific engineering issues.
3. **How are Plotly charts rendered?**
   * The backend processes SQLite records via Pandas aggregations, serializes them into structured Plotly figures, and transmits them to Plotly.js for responsive client-side rendering with no layout shift.
