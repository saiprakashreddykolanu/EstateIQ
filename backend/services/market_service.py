from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROFILES_PATH = (
    PROJECT_ROOT
    / "ml"
    / "artifacts"
    / "zip_market_profiles_v1.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "artifacts"
    / "zip_market_kmeans_v1_metadata.json"
)


if not PROFILES_PATH.exists():
    raise FileNotFoundError(
        f"ZIP market profiles not found: {PROFILES_PATH}"
    )


if not METADATA_PATH.exists():
    raise FileNotFoundError(
        f"K-Means metadata not found: {METADATA_PATH}"
    )


MARKET_PROFILES = pd.read_csv(PROFILES_PATH)

with open(
    METADATA_PATH,
    "r",
    encoding="utf-8",
) as file:
    MARKET_METADATA = json.load(file)


def get_market_segment(zipcode: int):

    match = MARKET_PROFILES[
        MARKET_PROFILES["zipcode"] == zipcode
    ]

    if match.empty:
        return {
            "available": False,
            "zipcode": zipcode,
            "message": (
                "No historical market segment "
                "is available for this ZIP code."
            ),
        }

    row = match.iloc[0]

    return {
        "available": True,

        "zipcode": int(row["zipcode"]),

        "segment": str(
            row["market_segment"]
        ),

        "cluster": int(
            row["market_cluster"]
        ),

        "property_count": int(
            row["property_count"]
        ),

        "median_price": round(
            float(row["median_price"]),
            2,
        ),

        "median_price_per_sqft": round(
            float(
                row[
                    "median_price_per_sqft"
                ]
            ),
            2,
        ),

        "median_sqft_living": round(
            float(
                row[
                    "median_sqft_living"
                ]
            ),
            0,
        ),

        "median_grade": round(
            float(row["median_grade"]),
            1,
        ),

        "algorithm": "K-Means",

        "model_version": "1.0",

        "silhouette_score": round(
            float(
                MARKET_METADATA[
                    "silhouette_score"
                ]
            ),
            4,
        ),

        "market_reference": (
            "King County historical "
            "2014-2015 market"
        ),
    }