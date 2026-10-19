from fastapi import APIRouter

from backend.schemas.property import (
    PropertyInput,
)

from backend.services.market_service import (
    get_market_segment,
)

from backend.services.valuation_service import (
    explain_prediction,
    predict_value,
)

from backend.services.comparable_service import (
    get_comparables,
)


router = APIRouter(
    prefix="/api/v1"
)


# ---------------------------------------------------------
# XGBOOST VALUATION
# ---------------------------------------------------------

@router.post("/valuation")
def valuation(
    property_input: PropertyInput,
):

    property_data = (
        property_input.model_dump()
    )


    predicted_value = predict_value(
        property_data
    )


    return {
        "estimated_value": round(
            predicted_value,
            2,
        ),

        "currency": "USD",

        "model": "XGBoost",

        "model_version": "1.0",

        "market_reference": (
            "King County historical "
            "2014-2015 market"
        ),
    }


# ---------------------------------------------------------
# KNN COMPARABLES
# ---------------------------------------------------------

@router.post("/comparables")
def comparables(
    property_input: PropertyInput,
):

    property_data = (
        property_input.model_dump()
    )


    results = get_comparables(
        property_data,
        n_neighbors=5,
    )


    return {
        "algorithm":
            "K-Nearest Neighbors",

        "candidate_strategy":
            "same_zipcode",

        "count":
            len(results),

        "comparables":
            results,
    }


# ---------------------------------------------------------
# XGBOOST SHAP EXPLANATION
# ---------------------------------------------------------

@router.post("/explain")
def explain_valuation(
    property_input: PropertyInput,
):

    property_data = (
        property_input.model_dump()
    )


    explanation = explain_prediction(
        property_data,
        top_n=8,
    )


    return explanation


# ---------------------------------------------------------
# COMPLETE ESTATEIQ ANALYSIS
# ---------------------------------------------------------

@router.post("/analyze")
def analyze_property(
    property_input: PropertyInput,
):

    property_data = (
        property_input.model_dump()
    )


    # -----------------------------------------------------
    # Algorithm 1: XGBoost
    # -----------------------------------------------------

    predicted_value = predict_value(
        property_data
    )


    # -----------------------------------------------------
    # Explainability layer: SHAP
    # -----------------------------------------------------

    valuation_explanation = (
        explain_prediction(
            property_data,
            top_n=8,
        )
    )


    # -----------------------------------------------------
    # Algorithm 2: KNN
    # -----------------------------------------------------

    comparable_properties = (
        get_comparables(
            property_data,
            n_neighbors=5,
        )
    )


    # -----------------------------------------------------
    # Algorithm 3: K-Means
    # -----------------------------------------------------

    market_analysis = (
        get_market_segment(
            property_data["zipcode"]
        )
    )


    # -----------------------------------------------------
    # Comparable median
    # -----------------------------------------------------

    comparable_prices = [
        item["sale_price"]
        for item
        in comparable_properties
    ]


    if comparable_prices:

        sorted_prices = sorted(
            comparable_prices
        )

        middle = (
            len(sorted_prices)
            // 2
        )

        median_comparable_price = (
            sorted_prices[middle]
        )

    else:

        median_comparable_price = None


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {

        "property": {

            "zipcode":
                property_data[
                    "zipcode"
                ],

            "bedrooms":
                property_data[
                    "bedrooms"
                ],

            "bathrooms":
                property_data[
                    "bathrooms"
                ],

            "sqft_living":
                property_data[
                    "sqft_living"
                ],

            "year_built":
                property_data[
                    "year_built"
                ],
        },


        "valuation": {

            "estimated_value":
                round(
                    predicted_value,
                    2,
                ),

            "currency":
                "USD",

            "algorithm":
                "XGBoost",

            "model_version":
                "1.0",

            "market_reference": (
                "King County historical "
                "2014-2015 market"
            ),
        },


        "valuation_explanation":
            valuation_explanation,


        "comparable_analysis": {

            "algorithm": (
                "K-Nearest Neighbors"
            ),

            "candidate_strategy": (
                "same_zipcode"
            ),

            "median_comparable_price":
                median_comparable_price,

            "comparables":
                comparable_properties,
        },


        "market_analysis":
            market_analysis,
    }