import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "hostel_complaints.db")

CATEGORIES = [
    "Mess / Food",
    "Wi-Fi / Internet",
    "Electricity",
    "Water Supply",
    "Cleaning",
    "Bathroom",
    "Room / Furniture",
    "Maintenance",
    "Security",
    "Other"
]

BLOCKS = ["Block A", "Block B", "Block C", "Block D", "Block E"]

SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]

SAMPLE_STUDENTS = [
    ("Aarav Sharma", "CS2023-014", "9876543210", "aarav.sharma@hostel.edu"),
    ("Diya Patel", "EC2023-089", "9876543211", "diya.patel@hostel.edu"),
    ("Rohan Mehta", "ME2022-045", "9876543212", "rohan.mehta@hostel.edu"),
    ("Ananya Verma", "CS2024-102", "9876543213", "ananya.verma@hostel.edu"),
    ("Vikram Singh", "EE2023-033", "9876543214", "vikram.singh@hostel.edu"),
    ("Sneha Nair", "IT2024-055", "9876543215", "sneha.nair@hostel.edu"),
    ("Karthik Reddy", "CS2022-120", "9876543216", "karthik.reddy@hostel.edu"),
    ("Pooja Joshi", "CE2023-078", "9876543217", "pooja.joshi@hostel.edu"),
    ("Arjun Gupta", "ME2024-019", "9876543218", "arjun.gupta@hostel.edu"),
    ("Tanvi Kulkarni", "EC2022-094", "9876543219", "tanvi.kulkarni@hostel.edu"),
    ("Rahul Sen", "IT2023-061", "9876543220", "rahul.sen@hostel.edu"),
    ("Ishita Roy", "CS2024-082", "9876543221", "ishita.roy@hostel.edu"),
    ("Siddharth Das", "EE2022-051", "9876543222", "siddharth.das@hostel.edu"),
    ("Meera Nambiar", "BT2023-027", "9876543223", "meera.nambiar@hostel.edu"),
    ("Aditya Malhotra", "CS2023-115", "9876543224", "aditya.malhotra@hostel.edu"),
]

SAMPLE_ISSUES = {
    "Mess / Food": [
        ("Dinner food quality degraded; dal undercooked and roti cold", "The dinner served on weekday evenings has been sub-standard, with dal frequently undercooked and rotis served cold.", "Mess Committee / Catering"),
        ("Breakfast timings inconsistent and milk ran out early", "Breakfast counter was closed 15 minutes before official time and milk was depleted before 8:30 AM.", "Mess Supervisor"),
        ("Unhygienic drinking water dispenser near mess washbasin", "Water cooler filter appears choked with sediments; needs urgent replacement.", "Hostel Maintenance & Mess"),
        ("Mess food seasoning excessively spicy; student health affected", "Several students reported stomach upset due to unusually high chili/oil levels in lunch gravies.", "Mess Warden"),
        ("Fly and insect netting torn near salad counter", "Kitchen window mosquito mesh has torn, allowing insects inside food preparation area.", "Sanitation Team")
    ],
    "Wi-Fi / Internet": [
        ("Wi-Fi router on 2nd floor dropping connection intermittently", "Access Point AP-B2 frequently reboots under load; packet loss over 40% during study hours.", "Network Admin / IT Cell"),
        ("DNS resolution failure on hostel student network", "Students cannot connect to educational portals or institutional mail via Wi-Fi subnet 192.168.10.x.", "IT Support Staff"),
        ("High latency and zero bandwidth during evening study hours (8-11 PM)", "Download speed drops below 0.5 Mbps every evening; difficult to complete online assignments.", "Campus Network Operations"),
        ("No signal in corner rooms (Rooms 210-215)", "Wi-Fi coverage dead zone detected in wing B corridor end; additional repeater required.", "IT Infrastructure"),
        ("MAC address authentication server timing out", "Portal login page throws 504 Gateway Timeout when registering new student laptops.", "IT Helpdesk")
    ],
    "Electricity": [
        ("Ceiling fan regulator burnt out and fan wobbling violently", "Regulator knob sparked and stopped working; fan running only at highest speed with severe rattle.", "Hostel Electrician - Mohan"),
        ("Fluorescent tube light flickering and buzzing continuously", "Main study tube light starter burned out; causes eye strain during night hours.", "Electrical Staff"),
        ("MCB circuit breaker tripping whenever water heater or laptop is plugged", "Room power breaker trips within 5 minutes of normal use; load imbalance suspected.", "Chief Electrician"),
        ("Power socket loose and sparking inside wall box", "Socket near study table has charred pin slots and produces sparks when plug inserted.", "Emergency Electrician"),
        ("Corridor emergency lighting battery dead during power cut", "Staircase and 3rd floor emergency LED lights failed to trigger during last night's outage.", "Electrical Maintenance")
    ],
    "Water Supply": [
        ("No water supply on 3rd floor since early morning", "Overhead tank pump stopped working or valve closed; zero pressure in faucets.", "Plumbing Department"),
        ("Tap leaking continuously under washbasin causing floor puddle", "Thread joint worn out; water dripping steadily and damaging wooden cupboard corner.", "Plumbing Staff - Ramesh"),
        ("Muddy and discolored water flowing from taps", "Water supply contains reddish silt and rust particles; overhead tank needs desilting.", "Estate & Water Works"),
        ("Low water pressure in flush cistern and showers", "Water takes over 25 minutes to refill toilet cistern; shower barely trickles.", "Hostel Plumber"),
        ("Hot water geyser pipeline leaking boiling water", "Safety valve pressure valve blowing steam and dripping hot water down the tile wall.", "Plumbing & Electrical Team")
    ],
    "Cleaning": [
        ("Common washroom cleaning skipped for two days", "Ground floor western toilets unclean; trash bins overflowing and no disinfectant used.", "Housekeeping Supervisor"),
        ("Corridor dustbins overflowing with food containers", "Foul odor spreading in wing C due to delayed collection by sanitation crew.", "Housekeeping Incharge"),
        ("Window grilles and corners covered in thick spider webs and dust", "End-corridor windows not wiped during regular cleaning cycles.", "Cleaning Staff"),
        ("Staircase floor slippery due to spilled beverage left uncleaned", "Accident hazard near 1st floor landing; immediate mopping needed.", "Sanitation Team"),
        ("Drainage grating blocked by fallen leaves outside hostel gate", "Rainwater pooling at hostel entrance path; requires sweeping and clearing.", "Campus Sanitation")
    ],
    "Bathroom": [
        ("Shower head detached and valve knob jammed", "Shower head fell off during use; knob cannot be shut tight without pliers.", "Plumbing Team"),
        ("Toilet flush handle broken and hanging loose", "Lever mechanism detached inside cistern; manual flush not functioning.", "Plumber - Santosh"),
        ("Exhaust fan in shared bathroom making screeching noise", "Motor bearing dry; fan vibrates loud enough to disturb adjacent rooms.", "Electrical Maintenance"),
        ("Bathroom floor drain clogged; water backing up during bath", "Soap scum and hair accumulation causing water stagnation up to ankles.", "Plumbing & Sanitation"),
        ("Mirror cracked and shelf bracket unfastened", "Glass shelf tilting downward, posing risk of falling toiletries.", "Hostel Carpenter / Repair")
    ],
    "Room / Furniture": [
        ("Study chair backrest broken and armrest loose", "Wooden screw joint fractured; chair unstable and unsafe to sit on.", "Hostel Carpentry - Dinesh"),
        ("Cupboard door hinges rusted and unable to latch shut", "Almirah door swinging open; lock hole misaligned with frame.", "Furniture Maintenance"),
        ("Bed frame wooden plank cracked along center support", "Mattress sagging significantly; replacement wooden slat needed.", "Carpentry Team"),
        ("Study desk laminate peeling off with sharp edge exposed", "Edge veneer chipped, tearing student clothes and paper sheets.", "Hostel Carpenter"),
        ("Window latch loose; window swings open in gusty wind", "Tower bolt missing screws; window slams at night.", "General Maintenance")
    ],
    "Maintenance": [
        ("Main entrance glass door closer malfunctioning", "Hydraulic closer leaking oil; door slams with heavy force.", "Hostel Estate Maintenance"),
        ("Balcony railing paint peeling and rust showing", "Iron railing corrosion visible on 4th floor; structural check recommended.", "Civil Engineering Dept"),
        ("Room ceiling damp patch and water seepage from upper floor", "Paint bubbling and flaking off near ceiling corner above study area.", "Civil Works & Waterproofing"),
        ("Lift door sensor misaligned on 2nd floor", "Elevator doors attempt to close before passengers finish exiting.", "Elevator AMC Technician"),
        ("Fire extinguisher inspection tag expired in corridor", "Corridor ABC dry powder cylinder inspection date elapsed by 3 months.", "Safety & Security Officer")
    ],
    "Security": [
        ("Hostel biometrics fingerprint scanner slow / rejected valid entries", "Scanner lens scratched; long queue forming during curfew check-in.", "Security Systems & IT"),
        ("CCTV camera outside Block B rear entrance has black screen", "Infrared camera feed offline in warden monitor room.", "Campus Security Dept"),
        ("Unauthorized delivery agent entered 2nd floor corridor", "Delivery personnel bypassed reception gate without signing visitor log.", "Chief Security Officer"),
        ("Room key duplicate stuck inside lock cylinder", "Brass key broken inside tumbler; student locked outside room.", "Warden Office / Locksmith"),
        ("Gate floodlight bulb blown, leaving path pitch dark", "Walkway between dining hall and Block C has zero lighting at night.", "Security & Electrical Team")
    ],
    "Other": [
        ("Stray dog entering hostel lobby through side open gate", "Animal scavenging near mess bins and barking during night hours.", "Estate Staff"),
        ("Courier parcel delivery counter disorganised and unattended", "Student parcels left unprotected on table without signature log.", "Student Welfare Office"),
        ("Laundry washing machine #3 shaking violently during spin cycle", "Common laundry unit rubber mounts damaged; machine walks across floor.", "Laundry AMC Team"),
        ("Gym equipment cable frayed in hostel recreational room", "Pulley cable wire strand snapped; potential injury risk.", "Sports & Gym Incharge"),
        ("Notice board glass panel cracked and pins missing", "Hostel announcement board cannot be locked.", "Hostel Caretaker")
    ]
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reseed=False):
    """Initializes tables and populates with realistic demo complaints if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_code TEXT UNIQUE NOT NULL,
        student_name TEXT NOT NULL,
        student_id TEXT NOT NULL,
        student_phone TEXT,
        student_email TEXT,
        block TEXT NOT NULL,
        room_number TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        resolved_at TEXT,
        resolution_time_days REAL,
        resolution_notes TEXT,
        assigned_to TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]

    if count == 0 or force_reseed:
        if force_reseed:
            cursor.execute("DELETE FROM complaints")
        seed_realistic_data(conn)

    # Set default settings if not exists
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('hostel_name', 'Grand Central University Hostel')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_name', 'Dr. S. K. Verma (Chief Warden)')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('emergency_contact', '+91 98765-43210')")

    conn.commit()
    conn.close()


def seed_realistic_data(conn):
    """
    Seeds ~248 realistic records spanning the past 90 days.
    Matches exact distribution targets:
    - Total: ~248
    - Resolved: ~184 (74%)
    - Pending: ~42 (17%)
    - In Progress: ~16 (7%)
    - Rejected: ~6 (2%)
    - Critical issues: exactly 12 active/recent critical issues
    - Block B has highest complaints (~30-35% more than average)
    - Realistic resolution times by category (e.g. Maintenance takes longer, Electricity fast)
    """
    random.seed(42)  # Deterministic seed for reproducible polished demo
    cursor = conn.cursor()

    now = datetime.now()
    total_records = 248

    # Category typical resolution days (mean, std)
    res_time_params = {
        "Mess / Food": (1.8, 0.5),
        "Wi-Fi / Internet": (2.2, 0.7),
        "Electricity": (1.4, 0.4),
        "Water Supply": (1.7, 0.5),
        "Cleaning": (1.2, 0.3),
        "Bathroom": (2.0, 0.6),
        "Room / Furniture": (2.8, 0.8),
        "Maintenance": (3.1, 0.9),
        "Security": (1.5, 0.4),
        "Other": (2.4, 0.6)
    }

    # Weight blocks so Block B has significantly more (~32% above average)
    block_weights = {
        "Block A": 0.18,
        "Block B": 0.32,  # Problematic block!
        "Block C": 0.19,
        "Block D": 0.16,
        "Block E": 0.15
    }

    category_weights = {
        "Wi-Fi / Internet": 0.20,
        "Mess / Food": 0.17,
        "Electricity": 0.15,
        "Water Supply": 0.14,
        "Bathroom": 0.10,
        "Room / Furniture": 0.08,
        "Cleaning": 0.06,
        "Maintenance": 0.05,
        "Security": 0.03,
        "Other": 0.02
    }

    # We want status distribution:
    # 184 Resolved, 42 Pending, 16 In Progress, 6 Rejected = 248 total
    statuses_pool = (
        ["Resolved"] * 184 +
        ["Pending"] * 42 +
        ["In Progress"] * 16 +
        ["Rejected"] * 6
    )
    random.shuffle(statuses_pool)

    # We want exactly 12 Critical issues, with others distributed
    # Critical: 12, High: 52, Medium: 114, Low: 70 = 248
    severities_pool = (
        ["Critical"] * 12 +
        ["High"] * 52 +
        ["Medium"] * 114 +
        ["Low"] * 70
    )
    random.shuffle(severities_pool)

    for i in range(total_records):
        complaint_id = f"C{1001 + i}"
        status = statuses_pool[i]
        severity = severities_pool[i]

        # Select student
        student = random.choice(SAMPLE_STUDENTS)

        # Select block based on weights
        block = random.choices(list(block_weights.keys()), weights=list(block_weights.values()))[0]

        # Room based on block (e.g., Block B -> B-101 to B-415)
        floor = random.randint(1, 4)
        room_num = random.randint(1, 20)
        room = f"{block.split()[1]}-{floor}{room_num:02d}"

        # Category based on weights
        category = random.choices(list(category_weights.keys()), weights=list(category_weights.values()))[0]

        # Issue template
        title, desc, default_assignee = random.choice(SAMPLE_ISSUES[category])

        # Date distribution: spread over last 90 days
        # Pending/In progress are biased towards more recent days (last 1-14 days)
        if status in ["Pending", "In Progress"]:
            days_ago = random.randint(0, 12)
        elif status == "Rejected":
            days_ago = random.randint(5, 60)
        else:  # Resolved
            days_ago = random.randint(3, 90)

        created_dt = now - timedelta(days=days_ago, hours=random.randint(1, 20), minutes=random.randint(0, 59))
        created_at_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")

        resolved_at_str = None
        resolution_days = None
        resolution_notes = None

        if status == "Resolved":
            mean_d, std_d = res_time_params.get(category, (2.0, 0.5))
            duration_days = max(0.4, round(random.gauss(mean_d, std_d), 1))
            res_dt = created_dt + timedelta(days=duration_days, hours=random.randint(1, 10))
            if res_dt > now:
                res_dt = now - timedelta(hours=random.randint(1, 12))
                duration_days = round(max(0.3, (res_dt - created_dt).total_seconds() / 86400), 1)
            resolved_at_str = res_dt.strftime("%Y-%m-%d %H:%M:%S")
            resolution_days = duration_days
            resolution_notes = f"Issue inspected on-site by {default_assignee}. Parts replaced/service rendered and verified by student."
        elif status == "Rejected":
            resolution_notes = "Duplicate submission or outside hostel administration jurisdiction. Student informed."

        cursor.execute("""
            INSERT INTO complaints (
                complaint_code, student_name, student_id, student_phone, student_email,
                block, room_number, category, title, description, severity, status,
                created_at, resolved_at, resolution_time_days, resolution_notes, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_id, student[0], student[1], student[2], student[3],
            block, room, category, title, desc, severity, status,
            created_at_str, resolved_at_str, resolution_days, resolution_notes, default_assignee
        ))

    conn.commit()


def get_all_complaints(search=None, category=None, block=None, severity=None, status=None, sort_by="date_desc", limit=None):
    """Fetches complaints with optional multi-criteria filtering and sorting."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if search:
        search_term = f"%{search.strip()}%"
        query += " AND (complaint_code LIKE ? OR student_name LIKE ? OR student_id LIKE ? OR room_number LIKE ? OR title LIKE ? OR description LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term, search_term, search_term])

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if block and block != "All":
        query += " AND block = ?"
        params.append(block)

    if severity and severity != "All":
        query += " AND severity = ?"
        params.append(severity)

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    # Sorting
    if sort_by == "date_desc":
        query += " ORDER BY datetime(created_at) DESC"
    elif sort_by == "date_asc":
        query += " ORDER BY datetime(created_at) ASC"
    elif sort_by == "priority":
        query += """ ORDER BY 
            CASE severity 
                WHEN 'Critical' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Medium' THEN 3 
                WHEN 'Low' THEN 4 
                ELSE 5 
            END ASC, datetime(created_at) DESC"""
    elif sort_by == "status":
        query += """ ORDER BY 
            CASE status 
                WHEN 'Critical' THEN 1
                WHEN 'Pending' THEN 2 
                WHEN 'In Progress' THEN 3 
                WHEN 'Resolved' THEN 4 
                ELSE 5 
            END ASC"""
    else:
        query += " ORDER BY datetime(created_at) DESC"

    if limit:
        query += f" LIMIT {int(limit)}"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_complaint_by_id(complaint_id):
    """Fetches single complaint by integer ID or complaint_code."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ? OR complaint_code = ?", (complaint_id, complaint_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_new_complaint(data):
    """Inserts a new complaint and returns the new complaint_code."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Determine next complaint code
    cursor.execute("SELECT MAX(id) FROM complaints")
    max_id = cursor.fetchone()[0] or 1000
    next_id = max_id + 1
    complaint_code = f"C{next_id}"

    created_at = data.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Default assigned staff based on category
    assignee_map = {
        "Mess / Food": "Mess Supervisor & Catering Committee",
        "Wi-Fi / Internet": "Campus IT Network Operations",
        "Electricity": "Hostel Electrician Department",
        "Water Supply": "Estate Plumbing Works",
        "Cleaning": "Housekeeping Head Incharge",
        "Bathroom": "Sanitation & Plumber Cell",
        "Room / Furniture": "Hostel Carpentry & Maintenance",
        "Maintenance": "Hostel Estate Office",
        "Security": "Chief Security Officer",
        "Other": "Hostel Warden Office"
    }
    assigned_to = assignee_map.get(data.get("category"), "Hostel Warden Office")

    cursor.execute("""
        INSERT INTO complaints (
            complaint_code, student_name, student_id, student_phone, student_email,
            block, room_number, category, title, description, severity, status,
            created_at, assigned_to
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?)
    """, (
        complaint_code,
        data.get("student_name", "").strip(),
        data.get("student_id", "").strip(),
        data.get("student_phone", "").strip(),
        data.get("student_email", "").strip(),
        data.get("block", "Block A"),
        data.get("room_number", "").strip().upper(),
        data.get("category", "Other"),
        data.get("title", "").strip() or f"{data.get('category')} problem reported",
        data.get("description", "").strip(),
        data.get("severity", "Medium"),
        created_at,
        assigned_to
    ))

    conn.commit()
    conn.close()
    return complaint_code


def update_complaint_status(complaint_id, new_status, resolution_notes=None, assigned_to=None):
    """Updates status, resolved_at timestamp, and resolution notes."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch existing
    cursor.execute("SELECT * FROM complaints WHERE id = ? OR complaint_code = ?", (complaint_id, complaint_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    now = datetime.now()
    resolved_at = None
    res_days = None

    if new_status == "Resolved":
        resolved_at = now.strftime("%Y-%m-%d %H:%M:%S")
        created_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
        res_days = round(max(0.1, (now - created_dt).total_seconds() / 86400), 1)

    query = "UPDATE complaints SET status = ?"
    params = [new_status]

    if new_status == "Resolved":
        query += ", resolved_at = ?, resolution_time_days = ?"
        params.extend([resolved_at, res_days])
    elif new_status in ["Pending", "In Progress"]:
        # If moving back to in-progress or pending
        query += ", resolved_at = NULL, resolution_time_days = NULL"

    if resolution_notes is not None:
        query += ", resolution_notes = ?"
        params.append(resolution_notes)

    if assigned_to:
        query += ", assigned_to = ?"
        params.append(assigned_to)

    query += " WHERE id = ? OR complaint_code = ?"
    params.extend([complaint_id, complaint_id])

    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return True


def get_kpi_summary():
    """Computes headline KPIs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE severity = 'Critical'")
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE severity = 'Critical' AND status != 'Resolved'")
    critical_pending = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(resolution_time_days) FROM complaints WHERE status = 'Resolved' AND resolution_time_days IS NOT NULL")
    avg_res_row = cursor.fetchone()[0]
    avg_resolution_days = round(avg_res_row, 1) if avg_res_row else 2.1

    resolution_rate = round((resolved / total * 100), 1) if total > 0 else 0

    conn.close()
    return {
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "in_progress": in_progress,
        "critical": critical,
        "critical_pending": critical_pending,
        "avg_resolution_days": avg_resolution_days,
        "resolution_rate": resolution_rate
    }
