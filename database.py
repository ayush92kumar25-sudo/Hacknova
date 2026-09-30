import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "waste_management.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    # SHA-256 with salt for secure storage
    salt = "swachh_pulse_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table (Citizens and Administrators)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('Citizen', 'Administrator')) NOT NULL DEFAULT 'Citizen',
            phone TEXT,
            ward_number TEXT DEFAULT 'Ward 14',
            address TEXT,
            karma_points INTEGER DEFAULT 120,
            streak_days INTEGER DEFAULT 7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Waste Issues / Complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL, 
            location_text TEXT NOT NULL,
            ward_number TEXT DEFAULT 'Ward 14',
            latitude REAL,
            longitude REAL,
            image_url TEXT,
            resolved_image_url TEXT,
            upvotes INTEGER DEFAULT 0,
            status TEXT CHECK(status IN ('Pending', 'Assigned', 'In Progress', 'Resolved')) NOT NULL DEFAULT 'Pending',
            assigned_team TEXT,
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Waste Pickup Requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pickup_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            request_type TEXT NOT NULL,
            estimated_volume TEXT NOT NULL,
            waste_type TEXT NOT NULL,
            pickup_date DATE NOT NULL,
            address TEXT NOT NULL,
            ward_number TEXT DEFAULT 'Ward 14',
            contact_number TEXT NOT NULL,
            special_instructions TEXT,
            status TEXT CHECK(status IN ('Requested', 'Scheduled', 'Completed', 'Cancelled')) NOT NULL DEFAULT 'Requested',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # User Contribution Activity table (GitHub-style 365-day contribution squares)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_date DATE NOT NULL,
            activity_count INTEGER DEFAULT 1,
            activity_type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()

    # Pre-populate default Administrator and demo Citizen if not existing
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        admin_pass = hash_password("admin123")
        citizen_pass = hash_password("citizen123")
        
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, ward_number, address, karma_points, streak_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Nagar Nigam Sanitation Supervisor (Admin)", "admin@cleanwaste.org", admin_pass, "Administrator", "+91-98765-43210", "Zonal HQ - Ward 14", "Central Municipal Corporation Building, Civil Lines", 950, 42))
        admin_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, ward_number, address, karma_points, streak_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Aarav Sharma (Swachh Nagrik)", "citizen@cleanwaste.org", citizen_pass, "Citizen", "+91-98100-11223", "Ward 14 (Indiranagar)", "Flat 402, Shanti Kunj Apartments, Indiranagar", 340, 14))
        citizen_id = cursor.lastrowid

        # Insert realistic Indian context sample complaints
        sample_complaints = [
            (citizen_id, "Overflowing Community Dustbin near Sabzi Mandi", "The green and blue community bins near Gate 2 Vegetable Market are overflowing with rotten cabbage leaves and fruit peels, attracting stray cattle.", "Overflowing Bins", "Indiranagar Sector 4, Sabzi Mandi Gate 2", "Ward 14", 28.6139, 77.2090, "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=600&q=80", "Pending", None, None),
            (citizen_id, "Morning Door-to-Door Kachra Gaadi Delayed", "Nagar Nigam tipper vehicle (Swachhata Gadi) did not arrive in Lane 3 today for segregated wet/dry waste collection.", "Missed Collection", "Lane 3, Shanti Kunj Colony, Indiranagar", "Ward 14", 28.6150, 77.2110, None, "Assigned", "Safai Mitra Unit 6 (North Zone)", "Scheduled for afternoon catch-up collection trip."),
            (citizen_id, "Construction Malba Dumped on Roadside", "A tractor-trolley dumped dry concrete rubble, broken bricks, and plaster bags by the park boundary wall at night.", "Illegal Dumping", "Behind Mahatma Gandhi Community Park, Ward 14", "Ward 14", 28.6180, 77.2140, "https://images.unsplash.com/photo-1605600659908-0ef719419d41?auto=format&fit=crop&w=600&q=80", "In Progress", "Rapid Malba Lifter Crew #2", "Heavy hydraulic loader dispatched to clear sidewalk."),
            (citizen_id, "Post-Festive Floral & Single-Use Plastic Litter", "Flower garlands, coconut husks, and plastic chai cups scattered near Temple Chowk after yesterday's religious gathering.", "Garbage on Roads", "Shiv Mandir Chowk, Main Market Road", "Ward 14", 28.6135, 77.2075, "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=600&q=80", "Resolved", "Prabhat Pheri Sanitation Team", "Street swept clean; temple floral waste diverted to local composting pit.")
        ]

        cursor.executemany("""
            INSERT INTO complaints (user_id, title, description, category, location_text, ward_number, latitude, longitude, image_url, status, assigned_team, admin_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_complaints)

        # Insert sample bulk pickup requests (Indian cultural context: Society cleanout, festive debris, wedding hall waste)
        sample_pickups = [
            (citizen_id, "Society Collective E-Waste & Bulk Disposal", "2 Large Trolleys (~180 kg)", "Old CRT TVs, Computer monitors, Wooden Charpais", "2026-10-06", "Shanti Kunj Cooperative Housing Society, Gate 1", "Ward 14", "+91-98100-11223", "Guard room has gate clearance; collect from basement ramp.", "Scheduled"),
            (citizen_id, "Residential Malba & Home Renovation Rubble", "Mini-Truckload (~450 kg)", "Brick pieces, dry plaster, discarded tiles", "2026-10-14", "House #28, Block B, Indiranagar", "Ward 14", "+91-98100-11223", "Keep dust tarpaulin ready. Contact guard on arrival.", "Requested")
        ]

        cursor.executemany("""
            INSERT INTO pickup_requests (user_id, request_type, estimated_volume, waste_type, pickup_date, address, ward_number, contact_number, special_instructions, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_pickups)

        # Seed GitHub-style 365-day contribution activity squares for citizen
        today = datetime.now().date()
        activities = []
        for days_back in range(120, 0, -1):
            act_date = today - timedelta(days=days_back)
            # Random realistic activity frequency
            if random.random() > 0.45:
                count = random.choice([1, 2, 3, 4])
                act_type = random.choice(["Segregation Verified", "Complaint Reported", "Quiz Completed", "Compost Recorded"])
                activities.append((citizen_id, act_date.strftime("%Y-%m-%d"), count, act_type))

        cursor.executemany("""
            INSERT INTO user_activities (user_id, activity_date, activity_count, activity_type)
            VALUES (?, ?, ?, ?)
        """, activities)

        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Indian Swachhata database initialized successfully.")
