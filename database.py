import sqlite3

def setup_database():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    # Job Descriptions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jds (
        jd_id INTEGER PRIMARY KEY,
        jd_text TEXT,
        keywords TEXT
    )
    ''')
    
    # CVs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cvs (
        cv_id INTEGER PRIMARY KEY,
        cv_text TEXT,
        keywords TEXT
    )
    ''')
    
    # Matches (ATS scores)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY,
        jd_id INTEGER,
        cv_id INTEGER,
        ats_score FLOAT
    )
    ''')
    
    conn.commit()
    conn.close()

setup_database()