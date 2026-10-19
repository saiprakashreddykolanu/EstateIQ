from pathlib import Path

import joblib
import pandas as pd
import shap


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "artifacts"
    / "valuation_xgb_v1.joblib"
)


FEATURES = [
    "bedrooms",
    "bathrooms",
    "sqft_living",
    "sqft_lot",
    "floors",
    "waterfront",
    "view",
    "condition",
    "grade",
    "sqft_above",
    "sqft_basement",
    "yr_built",
    "yr_renovated",
    "zipcode",
    "lat",
    "long",
    "sqft_living15",
    "sqft_lot15",
    "property_age",
    "was_renovated",
    "has_basement",
    "basement_value_missing",
    "waterfront_missing",
    "view_missing",
    "renovation_value_missing",
    "basement_ratio",
    "lot_to_living_ratio",
]


FEATURE_DISPLAY_NAMES = {
    "bedrooms": "Bedrooms",
    "bathrooms": "Bathrooms",
    "sqft_living": "Living Area",
    "sqft_lot": "Lot Size",
    "floors": "Floors",
    "waterfront": "Waterfront",
    "view": "View Quality",
    "condition": "Property Condition",
    "grade": "Property Grade",
    "sqft_above": "Above-Ground Living Area",
    "sqft_basement": "Basement Area",
    "yr_built": "Year Built",
    "yr_renovated": "Year Renovated",
    "zipcode": "ZIP Code",
    "lat": "Latitude",
    "long": "Longitude",
    "sqft_living15": "Nearby Home Size",
    "sqft_lot15": "Nearby Lot Size",
    "property_age": "Property Age",
    "was_renovated": "Renovation Status",
    "has_basement": "Basement Presence",
    "basement_value_missing": "Basement Data Status",
    "waterfront_missing": "Waterfront Data Status",
    "view_missing": "View Data Status",
    "renovation_value_missing": "Renovation Data Status",
    "basement_ratio": "Basement-to-Living Ratio",
    "lot_to_living_ratio": "Lot-to-Living Ratio",
}


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"EstateIQ valuation model not found: {MODEL_PATH}"
    )


MODEL = joblib.load(MODEL_PATH)


# ---------------------------------------------------------
# SHAP EXPLAINER
# ---------------------------------------------------------

EXPLAINER = shap.TreeExplainer(MODEL)


def prepare_features(
    property_data: dict,
) -> pd.DataFrame:

    model_reference_year = 2015

    year_built = property_data[
        "year_built"
    ]

    year_renovated = property_data[
        "year_renovated"
    ]

    sqft_living = property_data[
        "sqft_living"
    ]

    sqft_lot = property_data[
        "sqft_lot"
    ]

    sqft_basement = property_data[
        "sqft_basement"
    ]


    property_age = max(
        model_reference_year
        - year_built,
        0,
    )


    was_renovated = int(
        year_renovated > 0
    )


    has_basement = int(
        sqft_basement > 0
    )


    basement_ratio = (
        sqft_basement
        / sqft_living
    )


    lot_to_living_ratio = (
        sqft_lot
        / sqft_living
    )


    features = {

        "bedrooms":
            property_data["bedrooms"],

        "bathrooms":
            property_data["bathrooms"],

        "sqft_living":
            sqft_living,

        "sqft_lot":
            sqft_lot,

        "floors":
            property_data["floors"],

        "waterfront":
            property_data["waterfront"],

        "view":
            property_data["view"],

        "condition":
            property_data["condition"],

        "grade":
            property_data["grade"],

        "sqft_above":
            property_data["sqft_above"],

        "sqft_basement":
            sqft_basement,

        "yr_built":
            year_built,

        "yr_renovated":
            year_renovated,

        "zipcode":
            property_data["zipcode"],

        "lat":
            property_data["latitude"],

        "long":
            property_data["longitude"],

        "sqft_living15":
            property_data[
                "sqft_living15"
            ],

        "sqft_lot15":
            property_data[
                "sqft_lot15"
            ],

        "property_age":
            property_age,

        "was_renovated":
            was_renovated,

        "has_basement":
            has_basement,

        # API values are explicitly supplied.
        "basement_value_missing": 0,
        "waterfront_missing": 0,
        "view_missing": 0,
        "renovation_value_missing": 0,

        "basement_ratio":
            basement_ratio,

        "lot_to_living_ratio":
            lot_to_living_ratio,
    }


    return pd.DataFrame(
        [features],
        columns=FEATURES,
    )


def predict_value(
    property_data: dict,
) -> float:

    X = prepare_features(
        property_data
    )

    prediction = MODEL.predict(X)[0]

    return float(prediction)


def explain_prediction(
    property_data: dict,
    top_n: int = 8,
) -> dict:

    """
    Generate a local SHAP explanation for one
    EstateIQ XGBoost prediction.

    Positive SHAP values increase the prediction.
    Negative SHAP values decrease the prediction.
    """

    X = prepare_features(
        property_data
    )


    prediction = float(
        MODEL.predict(X)[0]
    )


    shap_explanation = EXPLAINER(X)


    shap_values = (
        shap_explanation.values[0]
    )


    base_value = float(
        shap_explanation.base_values[0]
    )


    factors = []


    for feature, shap_value in zip(
        FEATURES,
        shap_values,
    ):

        feature_value = X.iloc[0][
            feature
        ]


        impact = float(
            shap_value
        )


        factors.append(
            {
                "feature":
                    feature,

                "display_name":
                    FEATURE_DISPLAY_NAMES.get(
                        feature,
                        feature,
                    ),

                "feature_value":
                    float(
                        feature_value
                    ),

                "impact":
                    round(
                        impact,
                        2,
                    ),

                "absolute_impact":
                    round(
                        abs(impact),
                        2,
                    ),

                "direction":
                    (
                        "increases"
                        if impact > 0
                        else
                        "decreases"
                        if impact < 0
                        else
                        "neutral"
                    ),
            }
        )


    factors.sort(
        key=lambda item:
            item["absolute_impact"],
        reverse=True,
    )


    top_factors = factors[
        :top_n
    ]


    total_feature_impact = float(
        sum(shap_values)
    )


    reconstructed_prediction = (
        base_value
        + total_feature_impact
    )


    return {
        "available": True,

        "method":
            "SHAP TreeExplainer",

        "model":
            "XGBoost",

        "model_version":
            "1.0",

        "base_value":
            round(
                base_value,
                2,
            ),

        "total_feature_impact":
            round(
                total_feature_impact,
                2,
            ),

        "predicted_value":
            round(
                prediction,
                2,
            ),

        "reconstructed_prediction":
            round(
                reconstructed_prediction,
                2,
            ),

        "top_factors":
            top_factors,

        "interpretation": (
            "Positive SHAP values push "
            "the valuation higher than "
            "the model baseline, while "
            "negative SHAP values push "
            "the valuation lower."
        ),
    }