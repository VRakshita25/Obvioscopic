import sqlite3
from datetime import datetime

DB_NAME = "obvioscopic_cases.db"

def initialize_database():
    """Creates the case management table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            case_name TEXT NOT NULL,
            target_file_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            verdict TEXT DEFAULT 'UNANALYZED',
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_new_case(case_name, file_path):
    """Generates a new case record."""
    initialize_database()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    case_id = f"OBV-{timestamp}"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO cases (case_id, case_name, target_file_path, created_at)
        VALUES (?, ?, ?, ?)
    """, (case_id, case_name, file_path, date_str))
    
    conn.commit()
    conn.close()
    return case_id

def get_all_cases():
    """Fetches all past cases sorted by newest first."""
    initialize_database()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, case_name, target_file_path, created_at, verdict FROM cases ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows