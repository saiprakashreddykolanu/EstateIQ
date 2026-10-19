from pathlib import Path
import json

import joblib
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

ARTIFACT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "artifacts"
)


# Features used to describe each ZIP-code market.
CLUSTER_FEATURES = [
    "median_price",
    "median_price_per_sqft",
    "median_sqft_living",
    "median_grade",
    "median_bathrooms",
    "waterfront_rate",
    "renovation_rate",
]


def load_data():

    return pd.read_csv(DATA_PATH)


def build_zip_profiles(df):

    # Price per square foot is appropriate here
    # because clustering is descriptive rather
    # than predicting sale price.

    data = df.copy()

    data["price_per_sqft_cluster"] = (
        data["price"]
        / data["sqft_living"]
    )

    profiles = (
        data.groupby("zipcode")
        .agg(
            property_count=(
                "id",
                "size",
            ),

            median_price=(
                "price",
                "median",
            ),

            median_price_per_sqft=(
                "price_per_sqft_cluster",
                "median",
            ),

            median_sqft_living=(
                "sqft_living",
                "median",
            ),

            median_grade=(
                "grade",
                "median",
            ),

            median_bathrooms=(
                "bathrooms",
                "median",
            ),

            waterfront_rate=(
                "waterfront",
                "mean",
            ),

            renovation_rate=(
                "was_renovated",
                "mean",
            ),

            median_latitude=(
                "lat",
                "median",
            ),

            median_longitude=(
                "long",
                "median",
            ),
        )
        .reset_index()
    )

    return profiles


def evaluate_k(X_scaled):

    print("\nCLUSTER COUNT EVALUATION")
    print("=" * 60)

    results = []

    # We only have about 70 ZIP codes,
    # so keep the candidate range modest.

    for k in range(2, 7):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=50,
        )

        labels = model.fit_predict(
            X_scaled
        )

        score = silhouette_score(
            X_scaled,
            labels,
        )

        results.append(
            {
                "k": k,
                "silhouette": score,
                "inertia": model.inertia_,
            }
        )

        print(
            f"k={k} | "
            f"Silhouette={score:.4f} | "
            f"Inertia={model.inertia_:,.2f}"
        )

    return results


def main():

    print(
        "\nEstateIQ ZIP Market Segmentation"
    )

    print("=" * 60)

    df = load_data()

    print(
        f"Transactions: {len(df):,}"
    )

    profiles = build_zip_profiles(df)

    print(
        f"ZIP markets:  {len(profiles):,}"
    )

    print(
        f"Features:     {len(CLUSTER_FEATURES)}"
    )

    X = profiles[
        CLUSTER_FEATURES
    ].copy()

    if X.isna().any().any():

        raise ValueError(
            "ZIP clustering features "
            "contain missing values."
        )

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    results = evaluate_k(
        X_scaled
    )

    best = max(
        results,
        key=lambda result:
            result["silhouette"]
    )

    best_k = best["k"]

    print("\nBEST CONFIGURATION")
    print("=" * 60)

    print(
        f"k = {best_k}"
    )

    print(
        f"Silhouette = "
        f"{best['silhouette']:.4f}"
    )

    # ------------------------------------------
    # Train final model
    # ------------------------------------------

    model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=50,
    )

    profiles["market_cluster"] = (
        model.fit_predict(
            X_scaled
        )
    )

    # ------------------------------------------
    # Cluster profiles
    # ------------------------------------------

    cluster_summary = (
        profiles
        .groupby("market_cluster")
        .agg(
            zip_codes=(
                "zipcode",
                "size",
            ),

            properties=(
                "property_count",
                "sum",
            ),

            median_price=(
                "median_price",
                "median",
            ),

            median_price_per_sqft=(
                "median_price_per_sqft",
                "median",
            ),

            median_sqft_living=(
                "median_sqft_living",
                "median",
            ),

            median_grade=(
                "median_grade",
                "median",
            ),

            median_waterfront_rate=(
                "waterfront_rate",
                "median",
            ),
        )
        .reset_index()
    )

    print("\nCLUSTER PROFILES")
    print("=" * 90)

    print(
        cluster_summary.to_string(
            index=False
        )
    )

    # ------------------------------------------
    # Rank clusters by market price.
    #
    # These are descriptive labels only.
    # ------------------------------------------

    ordered_clusters = (
        cluster_summary
        .sort_values(
            "median_price"
        )
        ["market_cluster"]
        .tolist()
    )

    if best_k == 2:

        names = [
            "Core Market",
            "High-Value Market",
        ]

    elif best_k == 3:

        names = [
            "Value Market",
            "Established Market",
            "High-Value Market",
        ]

    elif best_k == 4:

        names = [
            "Value Market",
            "Core Market",
            "Premium Market",
            "Luxury Market",
        ]

    else:

        # Neutral labels when the data selects
        # more clusters than our named taxonomy.
        names = [
            f"Market Segment {i + 1}"
            for i in range(best_k)
        ]

    cluster_names = {
        int(cluster): name
        for cluster, name in zip(
            ordered_clusters,
            names,
        )
    }

    profiles["market_segment"] = (
        profiles["market_cluster"]
        .map(cluster_names)
    )

    print("\nZIP MARKET ASSIGNMENTS")
    print("=" * 90)

    display = profiles[
        [
            "zipcode",
            "property_count",
            "median_price",
            "median_price_per_sqft",
            "market_cluster",
            "market_segment",
        ]
    ].sort_values(
        [
            "market_cluster",
            "median_price",
        ]
    )

    print(
        display.to_string(
            index=False
        )
    )

    # ------------------------------------------
    # Save artifacts
    # ------------------------------------------

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        ARTIFACT_DIR
        / "zip_market_kmeans_v1.joblib"
    )

    scaler_path = (
        ARTIFACT_DIR
        / "zip_market_scaler_v1.joblib"
    )

    profiles_path = (
        ARTIFACT_DIR
        / "zip_market_profiles_v1.csv"
    )

    metadata_path = (
        ARTIFACT_DIR
        / "zip_market_kmeans_v1_metadata.json"
    )

    joblib.dump(
        model,
        model_path
    )

    joblib.dump(
        scaler,
        scaler_path
    )

    profiles.to_csv(
        profiles_path,
        index=False
    )

    metadata = {
        "algorithm": "KMeans",
        "version": "1.0",

        "segmentation_level":
            "ZIP code",

        "n_clusters":
            int(best_k),

        "silhouette_score":
            float(
                best["silhouette"]
            ),

        "features":
            CLUSTER_FEATURES,

        "cluster_names":
            cluster_names,

        "candidate_results":
            results,

        "cluster_summary":
            cluster_summary.to_dict(
                orient="records"
            ),
    }

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    print("\nARTIFACTS SAVED")
    print("=" * 60)

    print(model_path)
    print(scaler_path)
    print(profiles_path)
    print(metadata_path)

    print(
        "\nEstateIQ ZIP segmentation "
        "completed successfully."
    )


if __name__ == "__main__":
    main()