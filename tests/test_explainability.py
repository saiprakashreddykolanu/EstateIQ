def test_explain_endpoint(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/explain",
        json=valid_property,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["available"] is True

    assert (
        data["method"]
        == "SHAP TreeExplainer"
    )

    assert data["model"] == "XGBoost"

    assert data["model_version"] == "1.0"

    assert len(data["top_factors"]) > 0


def test_shap_reconstructs_prediction(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/explain",
        json=valid_property,
    )

    data = response.json()

    predicted = float(
        data["predicted_value"]
    )

    reconstructed = float(
        data[
            "reconstructed_prediction"
        ]
    )

    difference = abs(
        predicted - reconstructed
    )

    # SHAP reconstruction should reproduce
    # the model prediction extremely closely.
    #
    # Small floating-point differences are normal.

    assert difference < 2.0


def test_shap_feature_structure(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/explain",
        json=valid_property,
    )

    factors = (
        response
        .json()["top_factors"]
    )

    for factor in factors:

        assert "feature" in factor

        assert "display_name" in factor

        assert "feature_value" in factor

        assert "impact" in factor

        assert "absolute_impact" in factor

        assert factor["direction"] in [
            "increases",
            "decreases",
        ]