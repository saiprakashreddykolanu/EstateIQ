def test_valid_property_is_accepted(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/valuation",
        json=valid_property,
    )

    assert response.status_code == 200


def test_inconsistent_living_area_is_rejected(
    client,
    valid_property,
):

    payload = valid_property.copy()

    payload["sqft_above"] = 2450

    response = client.post(
        "/api/v1/valuation",
        json=payload,
    )

    assert response.status_code == 422

    body = response.text.lower()

    assert "sqft_living" in body
    assert "sqft_above" in body
    assert "sqft_basement" in body


def test_renovation_before_construction_is_rejected(
    client,
    valid_property,
):

    payload = valid_property.copy()

    payload["year_renovated"] = 1998

    response = client.post(
        "/api/v1/valuation",
        json=payload,
    )

    assert response.status_code == 422

    assert (
        "renovation year"
        in response.text.lower()
    )


def test_negative_living_area_is_rejected(
    client,
    valid_property,
):

    payload = valid_property.copy()

    payload["sqft_living"] = -100
    payload["sqft_above"] = -100

    response = client.post(
        "/api/v1/valuation",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_grade_is_rejected(
    client,
    valid_property,
):

    payload = valid_property.copy()

    payload["grade"] = 20

    response = client.post(
        "/api/v1/valuation",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_waterfront_value_is_rejected(
    client,
    valid_property,
):

    payload = valid_property.copy()

    payload["waterfront"] = 5

    response = client.post(
        "/api/v1/valuation",
        json=payload,
    )

    assert response.status_code == 422