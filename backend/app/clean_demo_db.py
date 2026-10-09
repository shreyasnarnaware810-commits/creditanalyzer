import sqlite3
import os

def cleanup_demo_db():
    db_path = "credence_ai.db"
    if not os.path.exists(db_path):
        print("Database file not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete demo users and related records
    cursor.execute("DELETE FROM users WHERE username IN ('officer_demo', 'meena_demo')")
    cursor.execute("DELETE FROM applications WHERE borrower_id IN ('usr_meena_demo_01', 'usr_officer_demo_01')")
    cursor.execute("DELETE FROM analysis_runs WHERE id = 'run_meena_demo_01'")
    cursor.execute("DELETE FROM uploaded_files WHERE id = 'file_meena_tx_01'")
    
    conn.commit()
    conn.close()
    print("Demo accounts (officer_demo, meena_demo) removed from database cleanly.")

if __name__ == "__main__":
    cleanup_demo_db()
