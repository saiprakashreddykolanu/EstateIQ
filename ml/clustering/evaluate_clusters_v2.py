from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "properties_clean.csv"
)


MODEL_FEATURES = [
    "log_price",
    "log_sqft_living",
    "log_sqft_lot",
    "bedrooms",
    "bathrooms",
    "grade",
    "condition",
    "lat",
    "long",
]


def prepare_features(df):

    data = df.copy()

    data["log_price"] = np.log1p(
        data["price"]
    )

    data["log_sqft_living"] = np.log1p(
        data["sqft_living"]
    )

    data["log_sqft_lot"] = np.log1p(
        data["sqft_lot"]
    )

    return data


def main():

    print("\nEstateIQ Cluster Evaluation V2")
    print("=" * 55)

    df = pd.read_csv(DATA_PATH)

    print(
        f"Properties: {len(df):,}"
    )

    df = prepare_features(df)

    X = df[MODEL_FEATURES].copy()

    if X.isna().any().any():
        raise ValueError(
            "Clustering features contain "
            "missing values."
        )

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    print(
        f"Features:   {len(MODEL_FEATURES)}"
    )

    print(
        "\nLog transformed:"
    )

    print(
        "  price"
    )

    print(
        "  sqft_living"
    )

    print(
        "  sqft_lot"
    )

    print(
        "\nEvaluating candidate cluster counts..."
    )

    print("-" * 55)

    results = []

    for k in range(2, 9):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=20,
        )

        labels = model.fit_predict(
            X_scaled
        )

        silhouette = silhouette_score(
            X_scaled,
            labels,
            sample_size=min(
                5000,
                len(X_scaled)
            ),
            random_state=42,
        )

        results.append(
            {
                "k": k,
                "silhouette": silhouette,
                "inertia": model.inertia_,
            }
        )

        print(
            f"k={k} | "
            f"Silhouette={silhouette:.4f} | "
            f"Inertia={model.inertia_:,.0f}"
        )

    best = max(
        results,
        key=lambda item: item["silhouette"]
    )

    print(
        "\nBEST V2 CONFIGURATION"
    )

    print("=" * 55)

    print(
        f"k = {best['k']}"
    )

    print(
        f"Silhouette = "
        f"{best['silhouette']:.4f}"
    )

    print(
        "\nV1 best silhouette: 0.2563"
    )

    improvement = (
        best["silhouette"] - 0.2563
    )

    print(
        f"Absolute change: "
        f"{improvement:+.4f}"
    )


if __name__ == "__main__":
    main()