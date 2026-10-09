import sqlite3
import os
import json
from contextlib import contextmanager
from app.config import settings

def connect_db(db_path: str = None):
    if db_path is None:
        db_path = settings.DATABASE_PATH
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db(db_path: str = None):
    conn = connect_db(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path: str = None):
    conn = connect_db(db_path)
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('officer', 'borrower')),
        full_name TEXT NOT NULL,
        is_demo_user INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Applications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        borrower_id TEXT NOT NULL,
        requested_amount REAL NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Submitted', 'Under Review', 'More Info Required', 'Approved', 'Declined')),
        assigned_officer_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(borrower_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(assigned_officer_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 3. Uploaded Files Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id TEXT PRIMARY KEY,
        application_id TEXT NOT NULL,
        uploader_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL CHECK(file_type IN ('transactions', 'utility')),
        checksum TEXT NOT NULL,
        row_count INTEGER NOT NULL,
        date_start TEXT,
        date_end TEXT,
        validation_summary TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('valid', 'invalid', 'warning')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE,
        FOREIGN KEY(uploader_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 4. Analysis Runs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_runs (
        id TEXT PRIMARY KEY,
        application_id TEXT NOT NULL,
        uploaded_file_ids TEXT NOT NULL,
        feature_schema_version INTEGER NOT NULL DEFAULT 1,
        model_version TEXT NOT NULL,
        score INTEGER NOT NULL,
        score_range_low INTEGER NOT NULL,
        score_range_high INTEGER NOT NULL,
        score_range_type TEXT NOT NULL DEFAULT 'heuristic',
        default_probability REAL NOT NULL,
        data_confidence TEXT NOT NULL CHECK(data_confidence IN ('High', 'Medium', 'Low')),
        output_metadata TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
    );
    """)

    # 5. Score Explanations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS score_explanations (
        id TEXT PRIMARY KEY,
        analysis_run_id TEXT NOT NULL,
        feature_name TEXT NOT NULL,
        feature_value REAL NOT NULL,
        contribution REAL NOT NULL,
        output_space TEXT NOT NULL DEFAULT 'score_points',
        direction TEXT NOT NULL CHECK(direction IN ('positive', 'negative')),
        technical_text TEXT NOT NULL,
        borrower_text TEXT NOT NULL,
        FOREIGN KEY(analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE
    );
    """)

    # 6. Counterfactuals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS counterfactuals (
        id TEXT PRIMARY KEY,
        analysis_run_id TEXT NOT NULL,
        feature_name TEXT NOT NULL,
        current_value REAL NOT NULL,
        target_value REAL NOT NULL,
        scenario_assumptions TEXT NOT NULL,
        plausibility_note TEXT NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE
    );
    """)

    # 7. Fraud Flags Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fraud_flags (
        id TEXT PRIMARY KEY,
        analysis_run_id TEXT NOT NULL,
        flag_type TEXT NOT NULL,
        severity TEXT NOT NULL CHECK(severity IN ('Low', 'Medium', 'High')),
        evidence_summary TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE
    );
    """)

    # 8. Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        actor_id TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        application_id TEXT NOT NULL,
        analysis_run_id TEXT,
        event_type TEXT NOT NULL,
        old_values TEXT,
        new_values TEXT,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(actor_id) REFERENCES users(id),
        FOREIGN KEY(application_id) REFERENCES applications(id)
    );
    """)

    # 9. Consent Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consent_records (
        id TEXT PRIMARY KEY,
        borrower_id TEXT NOT NULL,
        application_id TEXT NOT NULL,
        consent_version TEXT NOT NULL,
        purpose TEXT NOT NULL,
        given_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        withdrawn_at TIMESTAMP,
        FOREIGN KEY(borrower_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
    );
    """)

    # 10. Model Registry Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_registry (
        model_version TEXT PRIMARY KEY,
        model_type TEXT NOT NULL,
        dataset_version TEXT NOT NULL,
        seed INTEGER NOT NULL,
        metrics TEXT NOT NULL,
        feature_schema TEXT NOT NULL,
        trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 11. Fairness Runs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fairness_runs (
        id TEXT PRIMARY KEY,
        model_version TEXT NOT NULL,
        dataset_identifier TEXT NOT NULL,
        group_name TEXT NOT NULL,
        sample_count INTEGER NOT NULL,
        approval_rate REAL NOT NULL,
        score_average REAL NOT NULL,
        auc REAL NOT NULL,
        disparate_impact_ratio REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(model_version) REFERENCES model_registry(model_version)
    );
    """)

    conn.commit()
    conn.close()
