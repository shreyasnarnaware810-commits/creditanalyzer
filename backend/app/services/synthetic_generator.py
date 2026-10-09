import numpy as np
import pandas as pd
from typing import Tuple

FEATURE_NAMES = [
    "stable_monthly_cash_flow",
    "lean_month_cash_flow",
    "income_volatility",
    "activity_regularity",
    "counterparty_concentration",
    "utility_payment_punctuality",
    "month_end_buffer",
    "history_months",
    "seasonality_index",
    "recent_inflow_spike_ratio",
    "round_number_ratio"
]

def generate_synthetic_borrowers(n_borrowers: int = 5000, seed: int = 42) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    np.random.seed(seed)
    
    # Archetype proportions
    n_steady = int(n_borrowers * 0.35)
    n_seasonal = int(n_borrowers * 0.25)
    n_gig = int(n_borrowers * 0.20)
    n_single = int(n_borrowers * 0.10)
    n_suspicious = int(n_borrowers * 0.05)
    n_thin = n_borrowers - (n_steady + n_seasonal + n_gig + n_single + n_suspicious)
    
    rows = []
    groups = []
    
    # 1. Steady Shopkeepers
    for _ in range(n_steady):
        stable = np.random.uniform(25000, 80000)
        lean = stable * np.random.uniform(0.70, 0.90)
        volatility = np.random.uniform(0.10, 0.30)
        regularity = np.random.uniform(0.85, 1.0)
        concentration = np.random.uniform(0.05, 0.25)
        punctuality = np.random.uniform(0.80, 1.0)
        buffer = np.random.uniform(0.5, 2.0)
        history = np.random.uniform(12, 36)
        seasonality = np.random.uniform(1.0, 1.3)
        spike = np.random.uniform(0.9, 1.3)
        round_ratio = np.random.uniform(0.1, 0.3)
        rows.append([stable, lean, volatility, regularity, concentration, punctuality, buffer, history, seasonality, spike, round_ratio])
        groups.append("Steady Shopkeeper")
        
    # 2. Seasonal Sellers
    for _ in range(n_seasonal):
        stable = np.random.uniform(30000, 100000)
        lean = stable * np.random.uniform(0.20, 0.50)
        volatility = np.random.uniform(0.40, 0.85)
        regularity = np.random.uniform(0.60, 0.90)
        concentration = np.random.uniform(0.15, 0.40)
        punctuality = np.random.uniform(0.65, 0.95)
        buffer = np.random.uniform(0.2, 1.2)
        history = np.random.uniform(12, 36)
        seasonality = np.random.uniform(1.5, 2.8)
        spike = np.random.uniform(1.1, 2.0)
        round_ratio = np.random.uniform(0.1, 0.4)
        rows.append([stable, lean, volatility, regularity, concentration, punctuality, buffer, history, seasonality, spike, round_ratio])
        groups.append("Seasonal Seller")
        
    # 3. Gig Workers
    for _ in range(n_gig):
        stable = np.random.uniform(15000, 45000)
        lean = stable * np.random.uniform(0.40, 0.70)
        volatility = np.random.uniform(0.30, 0.60)
        regularity = np.random.uniform(0.70, 0.95)
        concentration = np.random.uniform(0.20, 0.50)
        punctuality = np.random.uniform(0.50, 0.90)
        buffer = np.random.uniform(0.1, 0.8)
        history = np.random.uniform(8, 24)
        seasonality = np.random.uniform(1.1, 1.6)
        spike = np.random.uniform(0.8, 1.5)
        round_ratio = np.random.uniform(0.2, 0.5)
        rows.append([stable, lean, volatility, regularity, concentration, punctuality, buffer, history, seasonality, spike, round_ratio])
        groups.append("Gig Worker")

    # 4. Single-Client Service Providers
    for _ in range(n_single):
        stable = np.random.uniform(35000, 90000)
        lean = stable * np.random.uniform(0.50, 0.80)
        volatility = np.random.uniform(0.20, 0.45)
        regularity = np.random.uniform(0.75, 0.95)
        concentration = np.random.uniform(0.75, 0.95) # High concentration
        punctuality = np.random.uniform(0.70, 1.0)
        buffer = np.random.uniform(0.4, 1.5)
        history = np.random.uniform(12, 30)
        seasonality = np.random.uniform(1.0, 1.4)
        spike = np.random.uniform(0.9, 1.4)
        round_ratio = np.random.uniform(0.1, 0.3)
        rows.append([stable, lean, volatility, regularity, concentration, punctuality, buffer, history, seasonality, spike, round_ratio])
        groups.append("Single-Client Provider")

    # 5. Suspicious Pattern Demos
    for _ in range(n_suspicious):
        stable = np.random.uniform(20000, 70000)
        lean = stable * np.random.uniform(0.10, 0.40)
        volatility = np.random.uniform(0.60, 1.20)
        regularity = np.random.uniform(0.40, 0.75)
        concentration = np.random.uniform(0.60, 0.90)
        punctuality = np.random.uniform(0.30, 0.70)
        buffer = np.random.uniform(0.05, 0.4)
        history = np.random.uniform(6, 18)
        seasonality = np.random.uniform(1.4, 2.5)
        spike = np.random.uniform(2.5, 4.5) # Suspicious spike
        round_ratio = np.random.uniform(0.65, 0.95) # Suspicious round numbers
        rows.append([stable, lean, volatility, regularity, concentration, punctuality, buffer, history, seasonality, spike, round_ratio])
        groups.append("Suspicious Pattern Demo")

    # 6. Thin-File Newcomers
    for _ in range(n_thin):
        stable = np.random.uniform(12000, 35000)
        lean = stable * np.random.uniform(0.30, 0.60)
        volatility = np.random.uniform(0.25, 0.55)
        regularity = np.random.uniform(0.50, 0.80)
        concentration = np.random.uniform(0.30, 0.70)
        punctuality = np.random.uniform(0.50, 0.85)
        buffer = np.random.uniform(0.1, 0.6)
        history = np.random.uniform(3, 6) # Thin history
        seasonality = np.random.uniform(1.0, 1.3)
        spike = np.random.uniform(0.8, 1.4)
        round_ratio = np.random.uniform(0.1, 0.4)
        rows.append([stable, lean, volatility, regularity, concentration, punctuality, buffer, history, seasonality, spike, round_ratio])
        groups.append("Thin-File Newcomer")

    X = pd.DataFrame(rows, columns=FEATURE_NAMES)
    
    # Define latent risk target (synthetic_default)
    # Logit formula based on domain assumptions
    logit = (
        0.8
        - 0.00004 * X["stable_monthly_cash_flow"]
        - 0.00006 * X["lean_month_cash_flow"]
        + 1.6 * X["income_volatility"]
        - 2.2 * X["activity_regularity"]
        + 1.5 * (X["counterparty_concentration"] - 0.4).clip(lower=0)
        - 2.5 * X["utility_payment_punctuality"]
        - 1.2 * X["month_end_buffer"]
        - 0.08 * X["history_months"]
        + 1.4 * (X["recent_inflow_spike_ratio"] > 2.2).astype(float)
        + 1.0 * (X["round_number_ratio"] > 0.6).astype(float)
        + np.random.normal(0, 0.4, size=n_borrowers)
    )
    
    prob_default = 1.0 / (1.0 + np.exp(-logit))
    y = (prob_default > 0.45).astype(int)
    
    return X, y, pd.Series(groups)
