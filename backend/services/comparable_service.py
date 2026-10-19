from pathlib import Path

import pandas as pd

from ml.comparables.knn_comparables import (
    find_comparables,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "properties_clean.csv"
)


PROPERTY_DATA = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)


def get_comparables(
    property_data: dict,
    n_neighbors: int = 5,
):

    year_built = property_data["year_built"]

    # Match the historical reference period
    # used by our V1 model.
    property_age = max(
        2015 - year_built,
        0
    )

    target_property = {
        "zipcode": property_data["zipcode"],
        "sqft_living": property_data["sqft_living"],
        "sqft_lot": property_data["sqft_lot"],
        "bedrooms": property_data["bedrooms"],
        "bathrooms": property_data["bathrooms"],
        "property_age": property_age,
        "grade": property_data["grade"],
        "condition": property_data["condition"],
    }

    comparables = find_comparables(
        df=PROPERTY_DATA,
        target_property=target_property,
        n_neighbors=n_neighbors,
    )

    results = []

    for _, row in comparables.iterrows():

        results.append(
            {
                "property_id": int(row["id"]),
                "sale_date": row["date"].date().isoformat(),
                "sale_price": round(float(row["price"]), 2),

                "zipcode": int(row["zipcode"]),

                "bedrooms": float(row["bedrooms"]),
                "bathrooms": float(row["bathrooms"]),

                "sqft_living": int(row["sqft_living"]),
                "sqft_lot": int(row["sqft_lot"]),

                "year_built": int(row["yr_built"]),

                "grade": int(row["grade"]),
                "condition": int(row["condition"]),

                "latitude": float(row["lat"]),
                "longitude": float(row["long"]),

                "knn_distance": round(
                    float(row["knn_distance"]),
                    4,
                ),

                "similarity_score": round(
                    float(row["similarity_score"]),
                    1,
                ),
            }
        )

    return results