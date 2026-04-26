from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def generate_data(n_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    tenures = rng.integers(1, 72, size=n_samples)
    monthly_charges = rng.normal(70, 25, size=n_samples).clip(18, 160)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], size=n_samples, p=[0.56, 0.23, 0.21])
    internet_service = rng.choice(["DSL", "Fiber", "None"], size=n_samples, p=[0.38, 0.49, 0.13])
    support_tickets = rng.poisson(1.8, size=n_samples).clip(0, 12)

    contract_risk = np.select(
        [contract == "Month-to-month", contract == "One year", contract == "Two year"],
        [0.9, 0.35, -0.15],
        default=0.0,
    )
    internet_risk = np.select(
        [internet_service == "Fiber", internet_service == "DSL", internet_service == "None"],
        [0.4, 0.15, -0.2],
        default=0.0,
    )

    linear_score = (
        -2.8
        + 0.03 * monthly_charges
        + 0.45 * support_tickets
        - 0.018 * tenures
        + contract_risk
        + internet_risk
        + rng.normal(0, 0.55, size=n_samples)
    )
    churn_probability = 1 / (1 + np.exp(-linear_score))
    churned = rng.binomial(1, churn_probability)

    return pd.DataFrame(
        {
            "tenure_months": tenures,
            "monthly_charges": monthly_charges.round(2),
            "contract_type": contract,
            "internet_service": internet_service,
            "support_tickets": support_tickets,
            "churned": churned,
        }
    )


def build_pipeline() -> Pipeline:
    numeric_features = ["tenure_months", "monthly_charges", "support_tickets"]
    categorical_features = ["contract_type", "internet_service"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = LogisticRegression(max_iter=1000, random_state=42)

    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def evaluate(y_true: pd.Series, y_pred: np.ndarray, y_proba: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
        "roc_auc": roc_auc_score(y_true, y_proba),
    }


def main() -> None:
    data = generate_data()

    features = [
        "tenure_months",
        "monthly_charges",
        "contract_type",
        "internet_service",
        "support_tickets",
    ]
    target = "churned"

    x_train, x_test, y_train, y_test = train_test_split(
        data[features],
        data[target],
        test_size=0.2,
        random_state=42,
        stratify=data[target],
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    metrics = evaluate(y_test, predictions, probabilities)

    print("Model performance:")
    for metric_name, value in metrics.items():
        print(f"- {metric_name}: {value:.4f}")

    output_dir = Path(__file__).parent / "artifacts"
    output_dir.mkdir(exist_ok=True)
    joblib.dump(pipeline, output_dir / "churn_pipeline.joblib")
    data.to_csv(output_dir / "sample_dataset.csv", index=False)

    print(f"\nSaved artifacts to: {output_dir}")


if __name__ == "__main__":
    main()