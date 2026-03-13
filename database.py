import sqlite3
import os

DB_NAME = "jefes.db"

def get_db_path():
    """Returns the absolute path to the database file."""
    # Store DB in the same folder as the script/executable
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # If running from PyInstaller temp dir, we might want it in the original dir
    # But for simplicity, let's assume it lives next to the exe or script
    if hasattr(sys, '_MEIPASS'):
        # If frozen, we want the DB next to the executable, not in temp dir
        base_dir = os.path.dirname(sys.executable)
    return os.path.join(base_dir, DB_NAME)

def init_db():
    """Initialize the database and table."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            equipo INTEGER,
            sector INTEGER,
            jefe TEXT,
            PRIMARY KEY (equipo, sector)
        )
    ''')
    conn.commit()
    conn.close()

def get_all_jefes():
    """Return all assignments as a dict {(eq, sec): chefe}."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT equipo, sector, jefe FROM assignments')
    rows = cursor.fetchall()
    conn.close()
    return {(r[0], r[1]): r[2] for r in rows}

def set_jefe(equipo, sector, jefe):
    """Update or insert a jefe assignment."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assignments (equipo, sector, jefe)
        VALUES (?, ?, ?)
        ON CONFLICT(equipo, sector) DO UPDATE SET jefe=excluded.jefe
    ''', (equipo, sector, jefe))
    conn.commit()
    conn.close()

def bulk_import(assignments):
    """
    Import a dictionary of {(eq, sec): jefe}.
    Only inserts/updates if entry doesn't exist or is different?
    For simplicity, we can just upsert all invalid/non-empty ones.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    data = [(eq, sec, jefe) for (eq, sec), jefe in assignments.items() if jefe]
    cursor.executemany('''
        INSERT INTO assignments (equipo, sector, jefe)
        VALUES (?, ?, ?)
        ON CONFLICT(equipo, sector) DO UPDATE SET jefe=excluded.jefe
    ''', data)
    
    conn.commit()
    conn.close()
