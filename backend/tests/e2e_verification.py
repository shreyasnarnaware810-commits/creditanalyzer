import sys
import httpx

BASE_URL = "http://127.0.0.1:8000"

def run_e2e_check():
    print("=== CREDENCE AI END-TO-END VERIFICATION SCRIPT ===")
    
    # 1. Seed Demo Data
    print("\n1. Seeding preloaded synthetic persona Meena...")
    r = httpx.post(f"{BASE_URL}/api/demo/seed")
    assert r.status_code == 200, f"Seed failed: {r.text}"
    seed_data = r.json()
    app_id = seed_data["application_id"]
    run_id = seed_data["analysis_run_id"]
    print(f"   Success: Seeded Application ID: {app_id}, Analysis Run ID: {run_id}")
    print(f"   Initial Score: {seed_data['score']}, Default Probability: {seed_data['default_probability']*100:.1f}%")

    # 2. Login as Officer
    print("\n2. Authenticating as Loan Officer (officer_demo)...")
    r = httpx.post(f"{BASE_URL}/api/auth/login", json={"username": "officer_demo", "password": "password123"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Success: JWT Access Token acquired.")

    # 3. Retrieve Application Details
    print("\n3. Retrieving application record...")
    r = httpx.get(f"{BASE_URL}/api/applications/{app_id}", headers=headers)
    assert r.status_code == 200, f"Get application failed: {r.text}"
    app_data = r.json()
    print(f"   Borrower: {app_data['borrower_name']}")
    print(f"   Requested Loan: INR {app_data['requested_amount']:,.2f}")

    # 4. Retrieve Analysis Run & Genuine SHAP Explanations
    print("\n4. Retrieving ML model scoring run & SHAP explanations...")
    r = httpx.get(f"{BASE_URL}/api/analysis/{run_id}", headers=headers)
    assert r.status_code == 200, f"Get analysis failed: {r.text}"
    ar = r.json()
    print(f"   Model Version: {ar['model_version']}")
    print(f"   Data Confidence: {ar['data']['data_confidence']}")
    print(f"   Stable Cash Flow: INR {ar['cashflow']['stable_monthly_cash_flow']:,.2f}")
    print(f"   Recommended Loan: INR {ar['loan_policy']['recommended_amount']:,.2f}")

    print("\n5. Verifying genuine SHAP feature contributions...")
    exps = ar["explanations"]
    assert len(exps) == 11, f"Expected 11 explanations, got {len(exps)}"
    top_pos = [e for e in exps if e["direction"] == "positive"][0]
    top_neg = [e for e in exps if e["direction"] == "negative"][0]
    print(f"   Top Positive Driver: {top_pos['feature_name']} (+{top_pos['contribution']:.1f} pts)")
    print(f"   Top Negative Driver: {top_neg['feature_name']} ({top_neg['contribution']:.1f} pts)")

    # 6. Run What-If Simulation
    print("\n6. Running What-If Counterfactual Scenario Simulation...")
    r = httpx.post(f"{BASE_URL}/api/analysis/whatif", json={
        "analysis_run_id": run_id,
        "stable_cash_flow": 75000.0,
        "utility_punctuality": 0.98
    }, headers=headers)
    assert r.status_code == 200, f"What-if failed: {r.text}"
    whatif = r.json()
    print(f"   Hypothetical Score: {whatif['hypothetical_score']} ({whatif['score_change']:+d} pts change)")
    print(f"   Hypothetical Default Prob: {whatif['hypothetical_default_probability']*100:.1f}%")
    print(f"   Hypothetical Recommended Loan: INR {whatif['hypothetical_recommended_amount']:,.2f}")

    # 7. Record Officer Decision & Test Mandatory Override Validation
    print("\n7. Testing mandatory override reason validation on officer decision...")
    r = httpx.post(f"{BASE_URL}/api/applications/{app_id}/decision", json={
        "status": "Approved",
        "approved_amount": 55000.0,
        "override_reason": "" # Empty override reason
    }, headers=headers)
    assert r.status_code == 400, "Validation failure expected for empty override reason"
    print("   Success: Backend rejected decision override without required reason as specified in blueprint.")

    print("\n8. Submitting valid officer decision with rationale...")
    r = httpx.post(f"{BASE_URL}/api/applications/{app_id}/decision", json={
        "status": "Approved",
        "approved_amount": 55000.0,
        "override_reason": "Applicant demonstrates 14 months of verified stall lease payments and 95% repeat customer cash flow.",
        "notes": "Approved under officer review tier."
    }, headers=headers)
    assert r.status_code == 200, f"Decision failed: {r.text}"
    print(f"   Success: Decision recorded: {r.json()['status']}")

    # 8. Check Audit Trail Log
    print("\n9. Verifying audit history trail...")
    r = httpx.get(f"{BASE_URL}/api/audit/{app_id}", headers=headers)
    assert r.status_code == 200, f"Audit failed: {r.text}"
    audit = r.json()
    assert len(audit) > 0
    dec_log = [log for log in audit if log['event_type'] == 'OFFICER_DECISION'][0]
    print(f"   Audit Log ID: {dec_log['id']}")
    print(f"   Event: {dec_log['event_type']} by {dec_log['actor_name']} ({dec_log['actor_role']})")
    print(f"   Recorded Override Rationale: '{dec_log['reason']}'")

    # 9. Check Fairness Metrics
    print("\n10. Checking synthetic fairness diagnostic panel...")
    r = httpx.get(f"{BASE_URL}/api/fairness", headers=headers)
    assert r.status_code == 200, f"Fairness failed: {r.text}"
    fairness = r.json()
    print(f"    Disparate Impact Ratio: {fairness['overall_disparate_impact']}")
    print(f"    Evaluated Groups: {len(fairness['groups'])} synthetic archetypes")

    print("\n=== ALL E2E VERIFICATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_e2e_check()
