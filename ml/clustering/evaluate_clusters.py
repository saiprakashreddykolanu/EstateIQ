from pathlib import Path

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


FEATURES = [
    "price",
    "sqft_living",
    "sqft_lot",
    "bedrooms",
    "bathrooms",
    "grade",
    "condition",
    "lat",
    "long",
]


def main():

    print("\nEstateIQ Cluster Evaluation")
    print("=" * 50)

    df = pd.read_csv(DATA_PATH)

    X = df[FEATURES].copy()

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    print(
        f"Properties: {len(df):,}"
    )

    print(
        f"Features:   {len(FEATURES)}"
    )

    print("\nEvaluating candidate cluster counts...")
    print("-" * 50)

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

        inertia = model.inertia_

        results.append(
            {
                "k": k,
                "silhouette": silhouette,
                "inertia": inertia,
            }
        )

        print(
            f"k={k} | "
            f"Silhouette={silhouette:.4f} | "
            f"Inertia={inertia:,.0f}"
        )

    print("\nBEST SILHOUETTE SCORE")
    print("=" * 50)

    best = max(
        results,
        key=lambda item: item["silhouette"]
    )

    print(
        f"k = {best['k']}"
    )

    print(
        f"Silhouette = "
        f"{best['silhouette']:.4f}"
    )


if __name__ == "__main__":
    main()