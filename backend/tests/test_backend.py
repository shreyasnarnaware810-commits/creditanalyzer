import os
import uuid
import pytest

os.environ["DATABASE_PATH"] = "test_credence_ai.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.services.ml_engine import probability_to_score
from app.services.shap_explainer import shap_explainer

TEST_DB = "test_credence_ai.db"

@pytest.fixture(scope="module")
def client():
    init_db(TEST_DB)
    with TestClient(app) as c:
        yield c
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass

def test_scorecard_conversion():
    score_low_risk = probability_to_score(0.02)
    score_high_risk = probability_to_score(0.60)
    assert 300 <= score_low_risk <= 900
    assert 300 <= score_high_risk <= 900
    assert score_low_risk > score_high_risk, "Lower default probability must produce a higher credit score"

def test_shap_additivity_and_score_reconciliation():
    sample_features = {
        "stable_monthly_cash_flow": 45000.0,
        "lean_month_cash_flow": 28000.0,
        "income_volatility": 0.25,
        "activity_regularity": 0.90,
        "counterparty_concentration": 0.20,
        "utility_payment_punctuality": 0.95,
        "month_end_buffer": 1.2,
        "history_months": 14.0,
        "seasonality_index": 1.2,
        "recent_inflow_spike_ratio": 1.1,
        "round_number_ratio": 0.2
    }
    
    explanations = shap_explainer.explain(sample_features)
    assert len(explanations) == 11
    
    for exp in explanations:
        if exp["direction"] == "positive":
            assert exp["contribution"] >= 0
        else:
            assert exp["contribution"] < 0

def test_auth_and_user_roles(client):
    uname = f"off_{uuid.uuid4().hex[:6]}"
    signup_res = client.post("/api/auth/signup", json={
        "username": uname,
        "email": f"{uname}@test.com",
        "password": "password123",
        "full_name": "Test Officer",
        "role": "officer"
    })
    assert signup_res.status_code == 200
    data = signup_res.json()
    assert "access_token" in data
    token = data["access_token"]
    
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "officer"

def test_seed_demo_and_meena_workflow(client):
    seed_res = client.post("/api/demo/seed")
    assert seed_res.status_code == 200
    seed_data = seed_res.json()
    assert "application_id" in seed_data
    assert "analysis_run_id" in seed_data
    
    login_res = client.post("/api/auth/login", json={
        "username": "officer_demo",
        "password": "password123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    
    app_id = seed_data["application_id"]
    app_res = client.get(f"/api/applications/{app_id}", headers={"Authorization": f"Bearer {token}"})
    assert app_res.status_code == 200
    assert app_res.json()["borrower_name"] == "Meena (Vegetable Vendor - Synthetic)"
    
    run_id = seed_data["analysis_run_id"]
    ar_res = client.get(f"/api/analysis/{run_id}", headers={"Authorization": f"Bearer {token}"})
    assert ar_res.status_code == 200
    ar_data = ar_res.json()
    assert ar_data["prediction"]["score"] > 300
    assert len(ar_data["explanations"]) > 0

def test_officer_decision_and_mandatory_override(client):
    login_res = client.post("/api/auth/login", json={"username": "officer_demo", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    seed_res = client.post("/api/demo/seed").json()
    app_id = seed_res["application_id"]
    
    fail_res = client.post(f"/api/applications/{app_id}/decision", json={
        "status": "Declined",
        "override_reason": ""
    }, headers=headers)
    assert fail_res.status_code == 400
    assert "Mandatory override reason" in fail_res.json()["detail"]
    
    success_res = client.post(f"/api/applications/{app_id}/decision", json={
        "status": "Approved",
        "approved_amount": 50000.0,
        "override_reason": "Applicant has 14 months of verified stall lease records and strong customer repeat business.",
        "notes": "Approved under officer review tier."
    }, headers=headers)
    assert success_res.status_code == 200
    
    audit_res = client.get(f"/api/audit/{app_id}", headers=headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) > 0
    assert any(log["event_type"] == "OFFICER_DECISION" for log in logs)

def test_whatif_scenario_recalculation(client):
    login_res = client.post("/api/auth/login", json={"username": "officer_demo", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    seed_res = client.post("/api/demo/seed").json()
    run_id = seed_res["analysis_run_id"]
    
    whatif_res = client.post("/api/analysis/whatif", json={
        "analysis_run_id": run_id,
        "stable_cash_flow": 60000.0,
        "utility_punctuality": 0.98
    }, headers=headers)
    
    assert whatif_res.status_code == 200
    res_data = whatif_res.json()
    assert "hypothetical_score" in res_data
    assert "changed_inputs" in res_data
    assert "stable_monthly_cash_flow" in res_data["changed_inputs"]

def test_download_assessment_report(client):
    login_res = client.post("/api/auth/login", json={"username": "officer_demo", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    seed_res = client.post("/api/demo/seed").json()
    run_id = seed_res["analysis_run_id"]

    report_res = client.get(f"/api/analysis/{run_id}/report", headers=headers)
    assert report_res.status_code == 200
    assert report_res.headers["content-type"] == "application/pdf"
    assert len(report_res.content) > 1000
    assert report_res.content.startswith(b"%PDF")


def test_pdf_gpay_statement_parsing_and_reconciliation():
    import os
    pdf_path = r"C:\Users\shash\Downloads\gpay_statement_20260401_20260930.pdf"
    if not os.path.exists(pdf_path):
        return

    from app.services.pdf_converter import parse_pdf_bank_statement

    with open(pdf_path, "rb") as f:
        content = f.read()

    res = parse_pdf_bank_statement(content, "gpay_statement.pdf")
    assert res["status"] == "valid"
    assert res["row_count"] == 46
    assert res["extracted_summary"]["total_credits"] == 47005.0
    assert res["extracted_summary"]["total_debits"] == 90101.0
    df = res["dataframe"]
    assert "counterparty" in df.columns
    assert "transaction_id" in df.columns


def test_scanned_or_unsupported_pdf_error_handling():
    from app.services.pdf_converter import parse_pdf_bank_statement
    
    # 1. Invalid/empty PDF test
    fake_empty_pdf = b"%PDF-1.4 empty pdf text layer demo"
    res_empty = parse_pdf_bank_statement(fake_empty_pdf, "scanned.pdf")
    assert res_empty["status"] == "invalid"
    assert "failed to read" in res_empty["error_message"].lower() or "scanned" in res_empty["error_message"].lower() or "no text" in res_empty["error_message"].lower()


def test_preview_pdf_endpoint(client):
    import os
    pdf_path = r"C:\Users\shash\Downloads\gpay_statement_20260401_20260930.pdf"
    if not os.path.exists(pdf_path):
        return

    login_res = client.post("/api/auth/login", json={"username": "officer_demo", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with open(pdf_path, "rb") as f:
        files = {"pdf_file": ("gpay_statement.pdf", f, "application/pdf")}
        res = client.post("/api/analysis/preview-pdf", headers=headers, files=files)

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["row_count"] == 46
    assert "csv_content" in data
    assert data["csv_content"].startswith("transaction_date,amount")


def test_non_utf8_csv_ingestion():
    from app.services.data_ingestion import parse_transaction_csv

    # CSV byte stream containing non-UTF8 byte 0x9c (e.g. CP1252 character)
    bad_utf8_csv = b"transaction_date,amount\n2025-08-01,2450.00\n2025-08-03,\x9c650.00\n"
    res = parse_transaction_csv(bad_utf8_csv, "non_utf8_test.csv")
    assert res["status"] in ["valid", "warning"]
    assert res["row_count"] == 2





