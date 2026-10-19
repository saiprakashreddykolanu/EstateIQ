import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def client():
    """
    FastAPI test client shared by the EstateIQ
    automated test suite.
    """

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_property():
    """
    Valid reference property used throughout
    the EstateIQ integration tests.

    ZIP 98052
    3,200 sqft living area
    No basement
    """

    return {
        "bedrooms": 4,
        "bathrooms": 3,
        "sqft_living": 3200,
        "sqft_lot": 7500,
        "floors": 2,
        "waterfront": 0,
        "view": 0,
        "condition": 3,
        "grade": 8,
        "sqft_above": 3200,
        "sqft_basement": 0,
        "year_built": 2005,
        "year_renovated": 0,
        "zipcode": 98052,
        "latitude": 47.67,
        "longitude": -122.12,
        "sqft_living15": 2400,
        "sqft_lot15": 7500,
    }