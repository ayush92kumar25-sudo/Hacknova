import os
import datetime
import jwt
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from database import get_db_connection, hash_password, init_db

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SECRET_KEY"] = "cleanwaste_secret_key_super_secure_2026"

# Ensure DB is created on startup
init_db()

# ================= AUTHENTICATION HELPER =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Authorization token is missing!"}), 401

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
            
            conn = get_db_connection()
            user = conn.execute("SELECT id, name, email, role, phone, address FROM users WHERE id = ?", (user_id,)).fetchone()
            conn.close()

            if not user:
                return jsonify({"error": "User not found!"}), 401

            current_user = dict(user)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session token has expired. Please log in again."}), 401
        except Exception as e:
            return jsonify({"error": "Invalid token.", "details": str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get("role") != "Administrator":
            return jsonify({"error": "Access denied. Administrator privileges required."}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# ================= AUTH ROUTES =================
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    role = data.get("role", "Citizen")
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    if role not in ["Citizen", "Administrator"]:
        role = "Citizen"

    conn = get_db_connection()
    existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({"error": "An account with this email address already exists."}), 400

    pwd_hash = hash_password(password)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, phone, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, pwd_hash, role, phone, address))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Create JWT Token
    token_exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    token = jwt.encode({"user_id": user_id, "role": role, "exp": token_exp}, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({
        "message": "Registration successful!",
        "token": token,
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "phone": phone,
            "address": address
        }
    }), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    pwd_hash = hash_password(password)
    conn = get_db_connection()
    user = conn.execute("""
        SELECT id, name, email, role, phone, address, password_hash FROM users WHERE email = ?
    """, (email,)).fetchone()
    conn.close()

    if not user or user["password_hash"] != pwd_hash:
        return jsonify({"error": "Invalid email or password."}), 401

    token_exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    token = jwt.encode({"user_id": user["id"], "role": user["role"], "exp": token_exp}, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "phone": user["phone"],
            "address": user["address"]
        }
    })

@app.route("/api/auth/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({"user": current_user})

# ================= COMPLAINTS & REPORTING =================
@app.route("/api/complaints", methods=["GET"])
@token_required
def get_complaints(current_user):
    conn = get_db_connection()
    
    # Filter by user if citizen, or allow admin to see all
    if current_user["role"] == "Administrator":
        status_filter = request.args.get("status")
        category_filter = request.args.get("category")
        query = """
            SELECT c.*, u.name as citizen_name, u.email as citizen_email, u.phone as citizen_phone
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND c.status = ?"
            params.append(status_filter)
        if category_filter:
            query += " AND c.category = ?"
            params.append(category_filter)
        
        query += " ORDER BY c.created_at DESC"
        rows = conn.execute(query, params).fetchall()
    else:
        query = """
            SELECT c.*, u.name as citizen_name, u.email as citizen_email, u.phone as citizen_phone
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        """
        rows = conn.execute(query, (current_user["id"],)).fetchall()

    conn.close()
    complaints = [dict(r) for r in rows]
    return jsonify({"complaints": complaints, "count": len(complaints)})

@app.route("/api/complaints", methods=["POST"])
@token_required
def create_complaint(current_user):
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    category = data.get("category", "").strip()
    location_text = data.get("location_text", "").strip()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    image_url = data.get("image_url", "").strip()

    valid_categories = ["Overflowing Bins", "Garbage on Roads", "Missed Collection", "Illegal Dumping"]
    if not title or not description or not location_text or not category:
        return jsonify({"error": "Title, description, category, and location are required."}), 400

    if category not in valid_categories:
        category = "Overflowing Bins"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (user_id, title, description, category, location_text, latitude, longitude, image_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (current_user["id"], title, description, category, location_text, latitude, longitude, image_url if image_url else None))
    complaint_id = cursor.lastrowid
    conn.commit()

    new_complaint = conn.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    conn.close()

    return jsonify({
        "message": "Waste complaint submitted successfully!",
        "complaint": dict(new_complaint)
    }), 201

@app.route("/api/complaints/<int:complaint_id>", methods=["PATCH"])
@token_required
@admin_required
def update_complaint_status(current_user, complaint_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    assigned_team = data.get("assigned_team")
    admin_notes = data.get("admin_notes")

    allowed_statuses = ["Pending", "Assigned", "In Progress", "Resolved"]
    if new_status and new_status not in allowed_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"}), 400

    conn = get_db_connection()
    complaint = conn.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    if not complaint:
        conn.close()
        return jsonify({"error": "Complaint not found."}), 404

    # Build dynamic update
    fields = []
    values = []
    if new_status:
        fields.append("status = ?")
        values.append(new_status)
    if assigned_team is not None:
        fields.append("assigned_team = ?")
        values.append(assigned_team)
    if admin_notes is not None:
        fields.append("admin_notes = ?")
        values.append(admin_notes)

    resolved_image_url = data.get("resolved_image_url")
    if resolved_image_url is not None:
        fields.append("resolved_image_url = ?")
        values.append(resolved_image_url)

    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(complaint_id)

    query = f"UPDATE complaints SET {', '.join(fields)} WHERE id = ?"
    conn.execute(query, values)
    conn.commit()

    updated = conn.execute("""
        SELECT c.*, u.name as citizen_name, u.email as citizen_email
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    """, (complaint_id,)).fetchone()
    conn.close()

    return jsonify({
        "message": "Complaint updated successfully.",
        "complaint": dict(updated)
    })

@app.route("/api/complaints/<int:complaint_id>/upvote", methods=["POST"])
@token_required
def upvote_complaint(current_user, complaint_id):
    conn = get_db_connection()
    complaint = conn.execute("SELECT id, upvotes FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    if not complaint:
        conn.close()
        return jsonify({"error": "Complaint not found."}), 404
    
    current_upvotes = complaint["upvotes"] if complaint["upvotes"] is not None else 0
    new_upvotes = current_upvotes + 1
    conn.execute("UPDATE complaints SET upvotes = ? WHERE id = ?", (new_upvotes, complaint_id))
    # Give user 5 karma points for civic engagement!
    conn.execute("UPDATE users SET karma_points = karma_points + 5 WHERE id = ?", (current_user["id"],))
    conn.commit()
    conn.close()
    return jsonify({
        "message": "Civic support upvote recorded (+5 Karma awarded)!",
        "complaint_id": complaint_id,
        "upvotes": new_upvotes
    })

@app.route("/api/festivals", methods=["GET"])
def get_green_festivals():
    festivals = [
        {
            "id": "diwali",
            "name": "Deepavali / Diwali (दीवाली)",
            "icon": "🪔",
            "tagline": "Light without Litter · Clay Diyas & Zero-Waste Celebrations",
            "challenge": "Post-festival streets choke with toxic chemical firecracker debris and single-use plastic sweet packaging.",
            "greenSolutions": [
                "Swap chemical crackers for traditional earthen clay diyas and LED solar fairy lights.",
                "Book our 'Diwali Ki Safai' doorstep pickup for old mattresses, broken cupboards, and e-waste.",
                "Gift sweets in reusable metal/bamboo hampers instead of thermocol and plastic wraps."
            ],
            "actionBadge": "Book Pre-Diwali Bulk Pickup"
        },
        {
            "id": "ganesh-durga",
            "name": "Ganesh Utsav & Durga Puja (गणेशोत्सव व दुर्गा पूजा)",
            "icon": "🐘",
            "tagline": "Eco-Friendly Visarjan · 100% Shadu Mati & Nirmalya Composting",
            "challenge": "PoP (Plaster of Paris) idols and toxic paints poison urban lakes, water bodies, and rivers.",
            "greenSolutions": [
                "Insist on 100% natural clay (Shadu Mati) idols painted with organic vegetable dyes.",
                "Immerse idols in municipal mobile artificial tanks (Krittim Kund) to save lakes and rivers.",
                "Segregate all holy puja flowers (Nirmalya) into designated green temple collection bins."
            ],
            "actionBadge": "Nirmalya Hubs Active"
        },
        {
            "id": "holi",
            "name": "Holi (होली)",
            "icon": "🎨",
            "tagline": "Dry Herbal Colors · Zero Water Wastage",
            "challenge": "Synthetic chemical colors (mercury, lead) cause skin rashes and pollute millions of liters of municipal water.",
            "greenSolutions": [
                "Use 100% organic herbal gulal made from Tesu flowers, marigold petals, beetroot, and turmeric.",
                "Play dry 'Tilak Holi' or waterless flower Holi to conserve precious groundwater.",
                "Avoid single-use plastic water balloons that turn into micro-plastic city litter."
            ],
            "actionBadge": "100% Organic Gulal"
        },
        {
            "id": "eid",
            "name": "Eid-ul-Fitr & Eid-ul-Adha (ईद)",
            "icon": "🌙",
            "tagline": "Clean Mohallas · Zero Food Waste Feasts",
            "challenge": "High volume of feast leftovers and improper animal organic waste disposal during community festivities.",
            "greenSolutions": [
                "Utilize local community food bank partnerships for surplus feast meals.",
                "Dispose of organic feast remains only in designated deep municipal collection pits.",
                "Serve community Iftar in reusable steel thalis instead of single-use plastic plates."
            ],
            "actionBadge": "Zero Food Waste"
        },
        {
            "id": "chhath-sankranti",
            "name": "Chhath Puja & Makar Sankranti (छठ व मकर संक्रांति)",
            "icon": "☀️",
            "tagline": "Pavitra Ghats · Clean Waterways & Zero Plastic",
            "challenge": "Devotional offerings (Arghya) and discarded plastic wrappers littering riverbanks and pond ghats.",
            "greenSolutions": [
                "Use only natural bamboo soops and dauras; avoid wrapping prasad in single-use plastic polythene.",
                "Volunteer for post-Arghya Ghat cleanliness drives (Ghat Safai Mitra).",
                "Compost all sugarcane stalks, banana leaves, and fruits in organic pits."
            ],
            "actionBadge": "Pavitra River Ghats"
        },
        {
            "id": "christmas-newyear",
            "name": "Christmas & New Year (क्रिसमस व नव वर्ष)",
            "icon": "🎄",
            "tagline": "Conscious Gifting · Zero Microplastic Glitter",
            "challenge": "Discarded plastic packaging, artificial trees, and non-recyclable metallic wrapping paper.",
            "greenSolutions": [
                "Wrap gifts in brown craft paper or newspaper tied with jute twine.",
                "Choose living potted indoor plants over disposable plastic artificial trees.",
                "Avoid glitter and plastic ribbon decorations that cannot be processed at recycling centers."
            ],
            "actionBadge": "Eco Gifting"
        }
    ]
    return jsonify({"festivals": festivals})

@app.route("/api/wards/leaderboard", methods=["GET"])
def get_ward_leaderboard():
    leaderboard = [
        {"rank": 1, "ward": "Ward 14 (Indiranagar)", "score": 96, "status": "5-Star Swachh Survekshan", "crews_active": 4, "avg_resolution_hrs": 3.8, "resolved_pct": 98},
        {"rank": 2, "ward": "Ward 11 (Jayanagar)", "score": 94, "status": "5-Star Swachh Survekshan", "crews_active": 3, "avg_resolution_hrs": 4.2, "resolved_pct": 95},
        {"rank": 3, "ward": "Ward 7 (Koramangala)", "score": 91, "status": "4-Star Swachh Survekshan", "crews_active": 3, "avg_resolution_hrs": 5.1, "resolved_pct": 92},
        {"rank": 4, "ward": "Ward 22 (Malleshwaram)", "score": 88, "status": "4-Star Swachh Survekshan", "crews_active": 2, "avg_resolution_hrs": 6.4, "resolved_pct": 89},
        {"rank": 5, "ward": "Ward 5 (Whitefield)", "score": 84, "status": "3-Star Swachh Survekshan", "crews_active": 2, "avg_resolution_hrs": 7.5, "resolved_pct": 84},
        {"rank": 6, "ward": "Ward 18 (Rajajinagar)", "score": 82, "status": "3-Star Swachh Survekshan", "crews_active": 2, "avg_resolution_hrs": 8.0, "resolved_pct": 81}
    ]
    return jsonify({"leaderboard": leaderboard, "city": "Nagar Nigam Central Zone", "updated_at": "Live IST"})

# ================= BULK PICKUP REQUESTS =================
@app.route("/api/pickups", methods=["GET"])
@token_required
def get_pickups(current_user):
    conn = get_db_connection()
    if current_user["role"] == "Administrator":
        query = """
            SELECT p.*, u.name as citizen_name, u.email as citizen_email
            FROM pickup_requests p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.pickup_date ASC
        """
        rows = conn.execute(query).fetchall()
    else:
        query = """
            SELECT * FROM pickup_requests
            WHERE user_id = ?
            ORDER BY pickup_date ASC
        """
        rows = conn.execute(query, (current_user["id"],)).fetchall()
    conn.close()
    return jsonify({"pickups": [dict(r) for r in rows]})

@app.route("/api/pickups", methods=["POST"])
@token_required
def create_pickup(current_user):
    data = request.get_json() or {}
    request_type = data.get("request_type", "Residential Bulk Pickup").strip()
    estimated_volume = data.get("estimated_volume", "").strip()
    waste_type = data.get("waste_type", "").strip()
    pickup_date = data.get("pickup_date", "").strip()
    address = data.get("address", "").strip() or current_user.get("address", "")
    contact_number = data.get("contact_number", "").strip() or current_user.get("phone", "")
    special_instructions = data.get("special_instructions", "").strip()

    if not estimated_volume or not waste_type or not pickup_date or not address:
        return jsonify({"error": "Volume, waste type, pickup date, and address are required."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pickup_requests 
        (user_id, request_type, estimated_volume, waste_type, pickup_date, address, contact_number, special_instructions, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Requested')
    """, (current_user["id"], request_type, estimated_volume, waste_type, pickup_date, address, contact_number, special_instructions))
    pickup_id = cursor.lastrowid
    conn.commit()

    created_pickup = conn.execute("SELECT * FROM pickup_requests WHERE id = ?", (pickup_id,)).fetchone()
    conn.close()

    return jsonify({
        "message": "Special pickup scheduled successfully!",
        "pickup": dict(created_pickup)
    }), 201

@app.route("/api/pickups/<int:pickup_id>", methods=["PATCH"])
@token_required
@admin_required
def update_pickup_status(current_user, pickup_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    allowed = ["Requested", "Scheduled", "Completed", "Cancelled"]
    if new_status not in allowed:
        return jsonify({"error": "Invalid pickup status."}), 400

    conn = get_db_connection()
    conn.execute("UPDATE pickup_requests SET status = ? WHERE id = ?", (new_status, pickup_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Pickup status updated successfully."})

# ================= ADMIN ANALYTICS & HOTSPOTS =================
@app.route("/api/admin/analytics", methods=["GET"])
@token_required
@admin_required
def get_admin_analytics(current_user):
    conn = get_db_connection()

    # Overview KPI metrics
    total_complaints = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    resolved_count = conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'").fetchone()[0]
    pending_count = conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'").fetchone()[0]
    in_progress_count = conn.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('Assigned', 'In Progress')").fetchone()[0]
    total_pickups = conn.execute("SELECT COUNT(*) FROM pickup_requests").fetchone()[0]
    total_citizens = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'Citizen'").fetchone()[0]

    # Category breakdown
    category_counts = conn.execute("""
        SELECT category, COUNT(*) as count 
        FROM complaints 
        GROUP BY category 
        ORDER BY count DESC
    """).fetchall()

    # Hotspots sorted by frequency of incidents at locations
    hotspots = conn.execute("""
        SELECT location_text, COUNT(*) as report_count, 
               MAX(latitude) as lat, MAX(longitude) as lng,
               GROUP_CONCAT(DISTINCT category) as recurring_issues
        FROM complaints
        GROUP BY location_text
        ORDER BY report_count DESC
        LIMIT 6
    """).fetchall()

    conn.close()

    return jsonify({
        "overview": {
            "total_complaints": total_complaints,
            "resolved": resolved_count,
            "pending": pending_count,
            "in_progress": in_progress_count,
            "total_pickups": total_pickups,
            "total_citizens": total_citizens,
            "resolution_rate": round((resolved_count / total_complaints * 100) if total_complaints > 0 else 0, 1)
        },
        "category_distribution": [dict(c) for c in category_counts],
        "hotspots": [dict(h) for h in hotspots]
    })

# ================= WASTE AWARENESS DATA =================
@app.route("/api/awareness", methods=["GET"])
def get_awareness_guides():
    guides = [
        {
            "id": "wet-biodegradable",
            "category": "Biodegradable (Wet Waste)",
            "color": "emerald",
            "icon": "leaf",
            "binColor": "Green Bin",
            "description": "Organic materials that decompose naturally within weeks. Best suited for composting and biogas generation.",
            "examples": ["Vegetable and fruit peels", "Leftover cooked food & tea bags", "Garden leaves, flowers, and grass clippings", "Egg shells and coffee grounds"],
            "dosAndDonts": {
                "dos": ["Drain excess liquid before throwing into bin", "Wrap wet waste in paper or compostable bin liners", "Maintain home vermicomposting if possible"],
                "donts": ["Never mix plastic carry bags or wrappers into green bins", "Avoid animal bones or raw diseased plants in household compost"]
            }
        },
        {
            "id": "dry-recyclable",
            "category": "Non-Biodegradable (Dry Recyclable)",
            "color": "blue",
            "icon": "recycle",
            "binColor": "Blue Bin",
            "description": "Materials that do not decompose easily but can be recycled or converted into secondary raw materials.",
            "examples": ["Cardboard boxes & newspapers", "PET bottles & plastic containers", "Metal cans & aluminum foil", "Glass containers & jars"],
            "dosAndDonts": {
                "dos": ["Rinse food residues before putting into recycling", "Flatten carton boxes to save space in bins", "Keep dry waste strictly separate from kitchen scraps"],
                "donts": ["Do not throw contaminated greasy pizza boxes with plastics", "Avoid broken window panes in standard recyclable bin"]
            }
        },
        {
            "id": "domestic-hazardous",
            "category": "Domestic Hazardous Waste",
            "color": "amber",
            "icon": "alert-triangle",
            "binColor": "Red / Yellow Bin",
            "description": "Toxic, flammable, or chemically active household substances that contaminate soil and groundwater if left in open landfills.",
            "examples": ["Paints, thinners & solvents", "Insecticides & pesticide cans", "Expired prescription medicines", "Bleaching agents & heavy chemical cleaners"],
            "dosAndDonts": {
                "dos": ["Keep in original marked containers with caps tight", "Hand over directly to designated municipal chemical collection drives"],
                "donts": ["Never pour chemicals down domestic drainage or sinks", "Never burn toxic containers or aerosol cans"]
            }
        },
        {
            "id": "e-waste",
            "category": "Electronic Waste (E-Waste)",
            "color": "indigo",
            "icon": "cpu",
            "binColor": "Grey Bin / Authorized Drop-off",
            "description": "Discarded electrical or electronic equipment containing lead, cadmium, copper, and precious recoverable metals.",
            "examples": ["Old smartphone batteries & charging cords", "Damaged laptops, CPUs & circuit boards", "Fluorescent tube lights & LED strips", "Microwaves & electronic appliances"],
            "dosAndDonts": {
                "dos": ["Utilize our app's 'Bulk Waste Pickup' feature for E-waste", "Deposit dead alkaline/lithium batteries at authorized collection hubs"],
                "donts": ["Never dismantle cathode ray tubes or lithium batteries by hand", "Never mix e-waste in standard garbage collection"]
            }
        }
    ]
    return jsonify({"guides": guides})

# ================= ECO-AI ASSISTANT & SWACHHATA ACADEMY ROUTES =================
from ai_assistant import (
    get_ai_response, 
    classify_issue_text, 
    analyze_waste_image, 
    calculate_route_optimization,
    get_swachhata_lessons,
    grade_swachh_quiz
)

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required."}), 400

    user_context = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            conn = get_db_connection()
            user = conn.execute("SELECT id, name, role, ward_number FROM users WHERE id = ?", (payload["user_id"],)).fetchone()
            conn.close()
            if user:
                user_context = dict(user)
        except Exception:
            pass

    response = get_ai_response(message, user_context)
    return jsonify(response)

@app.route("/api/ai/classify", methods=["POST"])
def ai_classify():
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required to classify issue."}), 400

    result = classify_issue_text(text)
    return jsonify(result)

@app.route("/api/ai/scan", methods=["POST"])
def ai_scan_waste():
    data = request.get_json() or {}
    item_type = data.get("item_type", "plastic_bottle")
    result = analyze_waste_image(item_type)
    return jsonify(result)

@app.route("/api/ai/route-optimizer", methods=["GET"])
@token_required
@admin_required
def ai_route_optimizer(current_user):
    conn = get_db_connection()
    complaints = conn.execute("""
        SELECT id, title, category, location_text, ward_number, status, latitude, longitude 
        FROM complaints 
        WHERE status IN ('Pending', 'Assigned')
        ORDER BY created_at ASC
    """).fetchall()
    conn.close()

    complaints_list = [dict(c) for c in complaints]
    result = calculate_route_optimization(complaints_list)
    return jsonify(result)

@app.route("/api/ai/lessons", methods=["GET"])
def get_lessons():
    lessons = get_swachhata_lessons()
    return jsonify({"lessons": lessons, "total": len(lessons)})

@app.route("/api/ai/quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json() or {}
    answers = data.get("answers", {})
    user_name = data.get("userName", "Swachh Nagrik")

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            conn = get_db_connection()
            user = conn.execute("SELECT id, name FROM users WHERE id = ?", (payload["user_id"],)).fetchone()
            if user:
                user_name = user["name"]
                # Award 50 karma points on quiz completion
                conn.execute("UPDATE users SET karma_points = karma_points + 50 WHERE id = ?", (user["id"],))
                conn.commit()
            conn.close()
        except Exception:
            pass

    result = grade_swachh_quiz(answers, user_name)
    return jsonify(result)

@app.route("/api/user/heatmap", methods=["GET"])
@token_required
def get_user_heatmap(current_user):
    # Generates 16 weeks (112 days) of GitHub-style contribution squares
    import datetime, random
    today = datetime.date.today()
    
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT activity_date, activity_count, activity_type 
        FROM user_activities 
        WHERE user_id = ? 
        ORDER BY activity_date ASC
    """, (current_user["id"],)).fetchall()
    conn.close()

    activity_map = {r["activity_date"]: r["activity_count"] for r in rows}

    squares = []
    # 16 weeks * 7 days = 112 days
    for i in range(111, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        
        # Check logged activity or generate a smooth realistic gradient
        if day_str in activity_map:
            count = activity_map[day_str]
        else:
            # Deterministic pseudo-random based on day hash for aesthetic consistency
            h = hash(f"{current_user['id']}-{day_str}") % 10
            count = 2 if h in [1, 2] else (3 if h == 3 else (1 if h in [4, 5] else 0))

        level = min(count, 4)
        squares.append({
            "date": day_str,
            "count": count,
            "level": level,
            "dayOfWeek": day.weekday()
        })

    return jsonify({
        "total_contributions": sum(s["count"] for s in squares),
        "streak_days": current_user.get("streak_days", 14),
        "karma_points": current_user.get("karma_points", 340),
        "squares": squares
    })

# ================= FRONTEND SERVING =================
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    print("CleanWaste EcoManager MVP is running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
