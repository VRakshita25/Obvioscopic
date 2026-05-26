import sqlite3

DB_NAME = "obvioscopic_cases.db"

def initialize_database():
    """Initializes the SQLite database with the correct modern schema structure."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table with all required structural columns including timestamp defaults
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_name TEXT NOT NULL,
            target_file_path TEXT NOT NULL,
            creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Run initialization immediately when imported
initialize_database()