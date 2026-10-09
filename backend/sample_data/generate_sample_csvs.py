import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

SAMPLE_DIR = os.path.dirname(__file__)

def generate_meena_transactions():
    np.random.seed(42)
    start_date = datetime(2025, 6, 1)
    rows = []
    balance = 12000.0
    tx_id = 1001
    
    for day in range(420):
        curr_date = start_date + timedelta(days=day)
        date_str = curr_date.strftime("%Y-%m-%d")
        month = curr_date.month
        
        # Seasonality factor (higher in festival months Oct-Dec)
        season_factor = 1.35 if month in [10, 11, 12] else (0.85 if month in [7, 8] else 1.0)
        
        # 1. Daily sales inflows (credits)
        num_sales = np.random.randint(1, 4)
        for _ in range(num_sales):
            amt = round(float(np.random.uniform(300, 1800) * season_factor), 2)
            balance += amt
            payer = f"CUST_{np.random.randint(101, 125)}"
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": amt,
                "transaction_type": "credit",
                "payer_id": payer,
                "description": "Vegetable Market Sales",
                "category": "sales",
                "balance_after_transaction": round(balance, 2)
            })
            tx_id += 1
            
        # 2. Restock debit (every 2-3 days)
        if day % 3 == 0:
            restock_amt = round(float(np.random.uniform(8000, 16000) * season_factor), 2)
            balance -= restock_amt
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": restock_amt,
                "transaction_type": "debit",
                "payee_id": "SUPPLIER_APMC_WHOLESALE",
                "description": "APMC Mandi Bulk Purchase",
                "category": "restock",
                "balance_after_transaction": round(balance, 2)
            })
            tx_id += 1

        # 3. Monthly Stall Rent (1st of month)
        if curr_date.day == 1:
            balance -= 4500.0
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": 4500.0,
                "transaction_type": "debit",
                "payee_id": "STALL_OWNER_01",
                "description": "Monthly Stall Lease Rent",
                "category": "rent",
                "balance_after_transaction": round(balance, 2)
            })
            tx_id += 1
            
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(SAMPLE_DIR, "meena_transactions.csv"), index=False)
    print("Created meena_transactions.csv")

def generate_meena_utility():
    rows = []
    start_date = datetime(2025, 6, 5)
    for i in range(14):
        bill_period = (start_date + timedelta(days=i*30)).strftime("%Y-%m")
        due_date = (start_date + timedelta(days=i*30 + 15)).strftime("%Y-%m-%d")
        pay_date = (start_date + timedelta(days=i*30 + 10)).strftime("%Y-%m-%d") # 5 days before due
        amt = round(float(np.random.uniform(1200, 2400)), 2)
        rows.append({
            "utility_account_id": "ELEC_MEENA_9821",
            "billing_period": bill_period,
            "due_date": due_date,
            "payment_date": pay_date,
            "amount_due": amt,
            "amount_paid": amt,
            "payment_status": "Paid",
            "source_verified": "True"
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(SAMPLE_DIR, "meena_utility.csv"), index=False)
    print("Created meena_utility.csv")

def generate_high_risk_transactions():
    np.random.seed(101)
    start_date = datetime(2026, 1, 1)
    rows = []
    balance = 3000.0
    tx_id = 5001
    
    for day in range(90): # Thin 3 months
        curr_date = start_date + timedelta(days=day)
        date_str = curr_date.strftime("%Y-%m-%d")
        
        if day % 7 == 0:
            amt = round(float(np.random.uniform(2000, 6000)), 2)
            balance += amt
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": amt,
                "transaction_type": "credit",
                "payer_id": "CLIENT_SINGLE",
                "description": "Freelance Payment",
                "category": "sales",
                "balance_after_transaction": round(balance, 2)
            })
            tx_id += 1
            
        if day % 4 == 0:
            amt = round(float(np.random.uniform(1500, 4500)), 2)
            balance -= amt
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": amt,
                "transaction_type": "debit",
                "payee_id": "VENDOR_MISC",
                "description": "Operating Expense",
                "category": "expense",
                "balance_after_transaction": round(balance, 2)
            })
            tx_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(SAMPLE_DIR, "high_risk_transactions.csv"), index=False)
    print("Created high_risk_transactions.csv")

def generate_fraud_flagged_transactions():
    np.random.seed(202)
    start_date = datetime(2025, 8, 1)
    rows = []
    balance = 5000.0
    tx_id = 9001
    
    # 6 months normal history
    for day in range(150):
        curr_date = start_date + timedelta(days=day)
        date_str = curr_date.strftime("%Y-%m-%d")
        if day % 5 == 0:
            balance += 5000.0
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": 5000.0, # Round amount
                "transaction_type": "credit",
                "payer_id": "SOLE_BUYER_INC",
                "description": "Consulting Fee",
                "category": "sales",
                "balance_after_transaction": balance
            })
            tx_id += 1
            
    # Recent spike (last 30 days)
    for day in range(150, 180):
        curr_date = start_date + timedelta(days=day)
        date_str = curr_date.strftime("%Y-%m-%d")
        if day % 2 == 0:
            balance += 25000.0 # Huge spike
            rows.append({
                "transaction_id": f"TX_{tx_id}",
                "transaction_date": date_str,
                "amount": 25000.0,
                "transaction_type": "credit",
                "payer_id": "SOLE_BUYER_INC",
                "description": "Consulting Fee Advance",
                "category": "sales",
                "balance_after_transaction": balance
            })
            tx_id += 1

    # Inject duplicate transaction ID
    rows.append(rows[-1].copy())
    
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(SAMPLE_DIR, "fraud_flagged_transactions.csv"), index=False)
    print("Created fraud_flagged_transactions.csv")

if __name__ == "__main__":
    generate_meena_transactions()
    generate_meena_utility()
    generate_high_risk_transactions()
    generate_fraud_flagged_transactions()
