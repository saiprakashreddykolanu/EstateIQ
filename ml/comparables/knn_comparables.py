from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "properties_clean.csv"
)


# Physical similarity features.
# Geography is handled separately.
KNN_FEATURES = [
    "sqft_living",
    "sqft_lot",
    "bedrooms",
    "bathrooms",
    "property_age",
    "grade",
    "condition",
]


def load_data():
    """Load cleaned EstateIQ property transactions."""

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["date"]
    )

    return df


def calculate_similarity(
    distances: np.ndarray
) -> np.ndarray:
    """
    Convert KNN distance into an intuitive
    0-100 similarity score.

    This is an EstateIQ presentation metric,
    not a statistical probability.
    """

    return 100 / (1 + distances)


def find_comparables(
    df: pd.DataFrame,
    target_property: dict,
    n_neighbors: int = 5,
):
    """
    Find comparable historical properties.

    Step 1:
        Restrict candidates to same ZIP code.

    Step 2:
        Standardize physical property features.

    Step 3:
        Use KNN to find nearest properties.
    """

    zipcode = target_property["zipcode"]

    candidates = df[
        df["zipcode"] == zipcode
    ].copy()

    if len(candidates) < n_neighbors:
        raise ValueError(
            f"Not enough comparable properties "
            f"in ZIP code {zipcode}. "
            f"Found only {len(candidates)}."
        )

    # ------------------------------------------
    # Prepare candidate feature matrix
    # ------------------------------------------

    X_candidates = candidates[
        KNN_FEATURES
    ].copy()

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X_candidates
    )

    # ------------------------------------------
    # Prepare target property
    # ------------------------------------------

    target_df = pd.DataFrame(
        [target_property]
    )

    X_target = target_df[
        KNN_FEATURES
    ]

    target_scaled = scaler.transform(
        X_target
    )

    # ------------------------------------------
    # KNN
    # ------------------------------------------

    knn = NearestNeighbors(
        n_neighbors=n_neighbors,
        metric="euclidean",
    )

    knn.fit(X_scaled)

    distances, indices = (
        knn.kneighbors(target_scaled)
    )

    distances = distances[0]
    indices = indices[0]

    similarity_scores = (
        calculate_similarity(distances)
    )

    # ------------------------------------------
    # Build response
    # ------------------------------------------

    comparable_rows = (
        candidates
        .iloc[indices]
        .copy()
    )

    comparable_rows["knn_distance"] = (
        distances
    )

    comparable_rows["similarity_score"] = (
        similarity_scores
    )

    output_columns = [
        "id",
        "date",
        "price",
        "zipcode",
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "yr_built",
        "grade",
        "condition",
        "lat",
        "long",
        "knn_distance",
        "similarity_score",
    ]

    return comparable_rows[
        output_columns
    ].reset_index(drop=True)


def print_comparables(
    target_property,
    comparables
):

    print("\nTARGET PROPERTY")
    print("=" * 50)

    print(
        f"ZIP Code:       "
        f"{target_property['zipcode']}"
    )

    print(
        f"Living Area:    "
        f"{target_property['sqft_living']:,.0f} sqft"
    )

    print(
        f"Lot Size:       "
        f"{target_property['sqft_lot']:,.0f} sqft"
    )

    print(
        f"Bedrooms:       "
        f"{target_property['bedrooms']}"
    )

    print(
        f"Bathrooms:      "
        f"{target_property['bathrooms']}"
    )

    print(
        f"Property Age:   "
        f"{target_property['property_age']} years"
    )

    print("\nTOP COMPARABLE PROPERTIES")
    print("=" * 80)

    for index, row in comparables.iterrows():

        print(
            f"\nComparable #{index + 1}"
        )

        print(
            f"Sale Price:     "
            f"${row['price']:,.0f}"
        )

        print(
            f"Sale Date:      "
            f"{row['date'].date()}"
        )

        print(
            f"Living Area:    "
            f"{row['sqft_living']:,.0f} sqft"
        )

        print(
            f"Lot Size:       "
            f"{row['sqft_lot']:,.0f} sqft"
        )

        print(
            f"Beds/Baths:     "
            f"{row['bedrooms']} / "
            f"{row['bathrooms']}"
        )

        print(
            f"Grade:          "
            f"{row['grade']}"
        )

        print(
            f"Condition:      "
            f"{row['condition']}"
        )

        print(
            f"Similarity:     "
            f"{row['similarity_score']:.1f}%"
        )


def main():

    print("\nEstateIQ Comparable Property Engine")
    print("=" * 50)

    df = load_data()

    print(
        f"Loaded {len(df):,} property transactions."
    )

    # Temporary demonstration property.
    #
    # Later these values will come from
    # the Next.js property analysis form.

    target_property = {
        "zipcode": 98052,
        "sqft_living": 2450,
        "sqft_lot": 7500,
        "bedrooms": 4,
        "bathrooms": 3,
        "property_age": 10,
        "grade": 8,
        "condition": 3,
    }

    comparables = find_comparables(
        df=df,
        target_property=target_property,
        n_neighbors=5,
    )

    print_comparables(
        target_property,
        comparables,
    )


if __name__ == "__main__":
    main()