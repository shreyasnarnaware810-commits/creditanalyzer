import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss, accuracy_score, precision_score, recall_score
from app.config import settings
from app.database import get_db
from app.services.synthetic_generator import generate_synthetic_borrowers, FEATURE_NAMES

MODEL_VERSION = "credence_gb_v1"
BASE_SCORE = 600
BASE_GOOD_TO_BAD_ODDS = 20.0
PDO = 40.0
FACTOR = PDO / np.log(2.0)
OFFSET = BASE_SCORE - FACTOR * np.log(BASE_GOOD_TO_BAD_ODDS)

# MVP heuristic bandwidth for score ranges
BAND_WIDTH = {"High": 15, "Medium": 30, "Low": 50}

def probability_to_score(p_default: float) -> int:
    p = float(np.clip(p_default, 1e-4, 1.0 - 1e-4))
    good_to_bad_odds = (1.0 - p) / p
    score = OFFSET + FACTOR * np.log(good_to_bad_odds)
    return int(np.clip(round(score), 300, 900))

def heuristic_score_range(score: int, data_confidence: str) -> Tuple[int, int]:
    width = BAND_WIDTH.get(data_confidence, 30)
    low = max(300, score - width)
    high = min(900, score + width)
    return low, high

class MLEngine:
    _instance = None

    def __init__(self):
        self.model = None
        self.metrics = {}
        self.artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.MODEL_ARTIFACTS_DIR)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.model_path = os.path.join(self.artifacts_dir, f"{MODEL_VERSION}.joblib")
        self.metrics_path = os.path.join(self.artifacts_dir, f"{MODEL_VERSION}_metrics.json")
        self.load_or_train()

    def load_or_train(self):
        if os.path.exists(self.model_path) and os.path.exists(self.metrics_path):
            self.model = joblib.load(self.model_path)
            with open(self.metrics_path, "r") as f:
                self.metrics = json.load(f)
        else:
            self.train_and_save()

    def train_and_save(self):
        X, y, groups = generate_synthetic_borrowers(n_borrowers=5000, seed=42)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, stratify=y, random_state=42
        )
        
        self.model = GradientBoostingClassifier(
            n_estimators=150, max_depth=3, learning_rate=0.05, random_state=42
        )
        self.model.fit(X_train, y_train)
        
        y_prob = self.model.predict_proba(X_test)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)
        
        auc = float(roc_auc_score(y_test, y_prob))
        brier = float(brier_score_loss(y_test, y_prob))
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        
        self.metrics = {
            "model_version": MODEL_VERSION,
            "synthetic_test_auc": round(auc, 4),
            "synthetic_test_brier": round(brier, 4),
            "synthetic_test_accuracy": round(acc, 4),
            "synthetic_test_precision": round(prec, 4),
            "synthetic_test_recall": round(rec, 4),
            "n_samples": len(y),
            "n_train": len(y_train),
            "n_test": len(y_test),
            "target": "synthetic_default"
        }
        
        joblib.dump(self.model, self.model_path)
        with open(self.metrics_path, "w") as f:
            json.dump(self.metrics, f, indent=2)
            
        # Record in DB registry if possible
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO model_registry
                    (model_version, model_type, dataset_version, seed, metrics, feature_schema)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    MODEL_VERSION,
                    "GradientBoostingClassifier",
                    "synthetic_v1",
                    42,
                    json.dumps(self.metrics),
                    json.dumps(FEATURE_NAMES)
                ))
        except Exception as e:
            print(f"Warning: Could not save model registry to DB: {e}")

    def predict(self, feature_dict: Dict[str, float], data_confidence: str = "Medium") -> Dict[str, Any]:
        # Form DataFrame with required column order
        row = [feature_dict.get(col, 0.0) for col in FEATURE_NAMES]
        df = pd.DataFrame([row], columns=FEATURE_NAMES)
        
        p_default = float(self.model.predict_proba(df)[0, 1])
        score = probability_to_score(p_default)
        low, high = heuristic_score_range(score, data_confidence)
        
        return {
            "score": score,
            "default_probability": round(p_default, 4),
            "probability_label": "synthetic-model estimate",
            "score_range": {
                "low": low,
                "high": high,
                "type": "heuristic"
            },
            "model_version": MODEL_VERSION
        }

ml_engine = MLEngine()
