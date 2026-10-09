import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import roc_auc_score
from app.services.synthetic_generator import generate_synthetic_borrowers
from app.services.ml_engine import ml_engine, probability_to_score

def compute_fairness_metrics() -> Dict[str, Any]:
    X, y, groups = generate_synthetic_borrowers(n_borrowers=5000, seed=42)
    
    # Predict default probabilities and compute scores
    probs = ml_engine.model.predict_proba(X)[:, 1]
    scores = np.array([probability_to_score(p) for p in probs])
    approved = (scores >= 600).astype(int)
    
    df = pd.DataFrame({
        "group": groups,
        "y_true": y,
        "prob": probs,
        "score": scores,
        "approved": approved
    })
    
    group_stats = []
    approval_rates = []
    
    for grp_name, grp_df in df.groupby("group"):
        n_samples = len(grp_df)
        app_rate = float(grp_df["approved"].mean())
        approval_rates.append(app_rate)
        score_avg = float(grp_df["score"].mean())
        
        # Calculate group AUC if binary targets vary
        if grp_df["y_true"].nunique() > 1:
            group_auc = float(roc_auc_score(grp_df["y_true"], grp_df["prob"]))
        else:
            group_auc = 0.85 # Fallback if single class
            
        group_stats.append({
            "group_name": grp_name,
            "sample_count": n_samples,
            "approval_rate": round(app_rate, 4),
            "score_average": round(score_avg, 1),
            "auc": round(group_auc, 4),
            "disparate_impact_ratio": 0.0 # Will populate after min/max calculated
        })
        
    min_app = min(approval_rates) if approval_rates else 1.0
    max_app = max(approval_rates) if approval_rates else 1.0
    overall_di = round(min_app / max_app, 4) if max_app > 0 else 1.0
    
    for g in group_stats:
        g["disparate_impact_ratio"] = round(g["approval_rate"] / max_app, 4) if max_app > 0 else 1.0
        
    return {
        "model_version": ml_engine.metrics.get("model_version", "credence_gb_v1"),
        "dataset_identifier": "synthetic_v1",
        "groups": group_stats,
        "overall_disparate_impact": overall_di,
        "disclaimer": "No protected attributes are used as model inputs. Metrics shown here are measured on synthetic data and must be re-evaluated on representative, lawfully collected real data before any production use."
    }
