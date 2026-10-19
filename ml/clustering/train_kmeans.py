from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "properties_clean.csv"
)

ARTIFACT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "artifacts"
)

MODEL_PATH = (
    ARTIFACT_DIR
    / "market_kmeans_v1.joblib"
)

SCALER_PATH = (
    ARTIFACT_DIR
    / "market_kmeans_scaler_v1.joblib"
)

METADATA_PATH = (
    ARTIFACT_DIR
    / "market_kmeans_v1_metadata.json"
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


def load_data():

    df = pd.read_csv(
        DATA_PATH
    )

    return df


def main():

    print("\nEstateIQ Market Segmentation")
    print("=" * 45)

    df = load_data()

    print(
        f"Loaded {len(df):,} properties."
    )

    X = df[FEATURES].copy()

    if X.isna().any().any():
        raise ValueError(
            "K-Means features contain missing values."
        )

    # ------------------------------------------
    # Standardization
    # ------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # ------------------------------------------
    # K-Means
    # ------------------------------------------

    number_of_clusters = 4

    model = KMeans(
        n_clusters=number_of_clusters,
        random_state=42,
        n_init=20,
    )

    print(
        f"\nTraining K-Means with "
        f"{number_of_clusters} clusters..."
    )

    clusters = model.fit_predict(
        X_scaled
    )

    df["market_cluster"] = clusters

    print("Training complete.")

    # ------------------------------------------
    # Evaluation
    # ------------------------------------------

    score = silhouette_score(
        X_scaled,
        clusters,
        sample_size=min(
            5000,
            len(X_scaled)
        ),
        random_state=42,
    )

    print(
        f"\nSilhouette Score: {score:.4f}"
    )

    # ------------------------------------------
    # Cluster profiles
    # ------------------------------------------

    profiles = (
        df.groupby("market_cluster")
        .agg(
            properties=("price", "size"),

            median_price=(
                "price",
                "median"
            ),

            median_sqft=(
                "sqft_living",
                "median"
            ),

            median_lot=(
                "sqft_lot",
                "median"
            ),

            median_bedrooms=(
                "bedrooms",
                "median"
            ),

            median_bathrooms=(
                "bathrooms",
                "median"
            ),

            median_grade=(
                "grade",
                "median"
            ),
        )
        .reset_index()
    )

    print("\nCLUSTER PROFILES")
    print("=" * 80)

    print(
        profiles.to_string(
            index=False
        )
    )

    # ------------------------------------------
    # Human-readable labels
    #
    # Important:
    # K-Means cluster IDs have no inherent
    # ordering, so rank them by median price.
    # ------------------------------------------

    ordered_clusters = (
        profiles
        .sort_values("median_price")
        ["market_cluster"]
        .tolist()
    )

    labels = [
        "Value Market",
        "Mid Market",
        "Premium Market",
        "Luxury Market",
    ]

    cluster_labels = {
        int(cluster): label
        for cluster, label
        in zip(
            ordered_clusters,
            labels
        )
    }

    df["market_segment"] = (
        df["market_cluster"]
        .map(cluster_labels)
    )

    print("\nMARKET SEGMENTS")
    print("=" * 80)

    for cluster in ordered_clusters:

        profile = profiles[
            profiles["market_cluster"]
            == cluster
        ].iloc[0]

        print(
            f"\nCluster {cluster} "
            f"→ {cluster_labels[int(cluster)]}"
        )

        print(
            f"Properties: "
            f"{int(profile['properties']):,}"
        )

        print(
            f"Median Price: "
            f"${profile['median_price']:,.0f}"
        )

        print(
            f"Median Living Area: "
            f"{profile['median_sqft']:,.0f} sqft"
        )

        print(
            f"Median Grade: "
            f"{profile['median_grade']:.1f}"
        )

    # ------------------------------------------
    # Save artifacts
    # ------------------------------------------

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    joblib.dump(
        scaler,
        SCALER_PATH
    )

    metadata = {
        "algorithm": "KMeans",
        "version": "1.0",
        "n_clusters": number_of_clusters,

        "features": FEATURES,

        "silhouette_score": float(score),

        "cluster_labels": cluster_labels,

        "profiles": profiles.to_dict(
            orient="records"
        ),
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print("\nArtifacts saved:")

    print(MODEL_PATH)
    print(SCALER_PATH)
    print(METADATA_PATH)

    print(
        "\nEstateIQ market segmentation complete."
    )


if __name__ == "__main__":
    main()