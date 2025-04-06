import sqlite3
from database import setup_database  # Import your database setup
from agents import extract_keywords, calculate_ats_score
from clean_data import clean_text  # Import cleaning function

def main():
    # Initialize database tables
    setup_database()
    
    # Example test data
    test_jd = "We need a Python developer with 5+ years of experience in Django and AWS."
    test_cv = "I have 6 years of experience in Python, Django, and cloud platforms like AWS."

    try:
        # Connect to database with context manager
        with sqlite3.connect('jobs.db') as conn:
            cursor = conn.cursor()

            # Process and save JD
            print("⏳ Processing Job Description...")
            jd_keywords = extract_keywords(clean_text(test_jd), "jd")
            cursor.execute('''
                INSERT INTO jds (jd_text, keywords)
                VALUES (?, ?)
            ''', (test_jd, ", ".join(jd_keywords)))
            jd_id = cursor.lastrowid
            print(f"✅ JD saved (ID: {jd_id})")

            # Process and save CV
            print("\n⏳ Processing CV...")
            cv_keywords = extract_keywords(clean_text(test_cv), "cv")
            cursor.execute('''
                INSERT INTO cvs (cv_text, keywords)
                VALUES (?, ?)
            ''', (test_cv, ", ".join(cv_keywords)))
            cv_id = cursor.lastrowid
            print(f"✅ CV saved (ID: {cv_id})")

            # Calculate and save match
            print("\n🧮 Calculating ATS Score...")
            ats_score, matched = calculate_ats_score(jd_keywords, cv_keywords)
            cursor.execute('''
                INSERT INTO matches (jd_id, cv_id, ats_score)
                VALUES (?, ?, ?)
            ''', (jd_id, cv_id, ats_score))
            print(f"✅ Match saved (JD: {jd_id}, CV: {cv_id})")

            # Commit transaction
            conn.commit()

            # Display results
            print(f"\n🎯 Final ATS Score: {ats_score}%")
            print("🔑 Matched Keywords:", ", ".join(matched))

    except sqlite3.Error as e:
        print(f"🚨 Database Error: {str(e)}")
    except Exception as e:
        print(f"🚨 General Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()