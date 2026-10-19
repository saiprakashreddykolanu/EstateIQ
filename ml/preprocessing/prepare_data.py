from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = (
    PROJECT_ROOT / "ml" / "data" / "raw" / "kc_house_data.csv"
)

PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "ml" / "data" / "processed" / "properties_clean.csv"
)


# --------------------------------------------------
# Required dataset columns
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "id",
    "date",
    "price",
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
]


# --------------------------------------------------
# Load
# --------------------------------------------------

def load_data(path: Path) -> pd.DataFrame:
    """Load raw housing data."""

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(path)

    print(f"Loaded rows: {len(df):,}")
    print(f"Original columns: {len(df.columns)}")

    return df


# --------------------------------------------------
# Validate
# --------------------------------------------------

def validate_columns(df: pd.DataFrame) -> None:
    """Check that required columns exist."""

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


# --------------------------------------------------
# Cleaning
# --------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean invalid or unusable records."""

    df = df.copy()

    rows_before = len(df)

    # ------------------------------------------
    # Parse transaction date
    # ------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # ------------------------------------------
    # Convert expected numeric columns
    # ------------------------------------------

    numeric_columns = [
        "price",
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
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # ------------------------------------------
    # Handle known missing-value fields
    # ------------------------------------------

    # Waterfront:
    # Preserve whether the original value was missing,
    # then use 0 as the V1 fallback.
    df["waterfront_missing"] = (
        df["waterfront"].isna()
    ).astype(int)

    waterfront_missing_count = int(
        df["waterfront"].isna().sum()
    )

    print(
        f"Missing waterfront values: "
        f"{waterfront_missing_count:,}"
    )

    df["waterfront"] = (
        df["waterfront"].fillna(0)
    )

    # View:
    # Preserve missingness and use the dataset median.
    df["view_missing"] = (
        df["view"].isna()
    ).astype(int)

    view_missing_count = int(
        df["view"].isna().sum()
    )

    view_median = df["view"].median()

    print(
        f"Missing view values: "
        f"{view_missing_count:,}"
    )

    print(
        f"View median used for imputation: "
        f"{view_median}"
    )

    df["view"] = (
        df["view"].fillna(view_median)
    )

    # Renovation year:
    # In this dataset, 0 represents no recorded renovation.
    # We preserve whether the source value itself was missing.
    df["renovation_value_missing"] = (
        df["yr_renovated"].isna()
    ).astype(int)

    renovation_missing_count = int(
        df["yr_renovated"].isna().sum()
    )

    print(
        f"Missing renovation-year values: "
        f"{renovation_missing_count:,}"
    )

    df["yr_renovated"] = (
        df["yr_renovated"].fillna(0)
    )
    # ------------------------------------------
    # Track missing basement values
    # ------------------------------------------

    df["basement_value_missing"] = (
        df["sqft_basement"].isna()
    ).astype(int)

    missing_basement_count = int(
        df["sqft_basement"].isna().sum()
    )

    print(
        f"Missing/non-numeric basement values: "
        f"{missing_basement_count:,}"
    )

    # For V1, preserve these properties.
    # Unknown basement square footage is filled with 0,
    # while basement_value_missing records that the
    # original value was unavailable.
    df["sqft_basement"] = (
        df["sqft_basement"].fillna(0)
    )

    # ------------------------------------------
    # Remove exact duplicate rows
    # ------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    print(
        f"Exact duplicate rows: "
        f"{duplicate_count:,}"
    )

    df = df.drop_duplicates()

    # ------------------------------------------
    # Essential fields
    # ------------------------------------------

    essential_columns = [
        "date",
        "price",
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "yr_built",
        "zipcode",
        "lat",
        "long",
    ]

    invalid_essential_count = int(
        df[essential_columns]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"Rows with missing essential values: "
        f"{invalid_essential_count:,}"
    )

    df = df.dropna(
        subset=essential_columns
    )

    # ------------------------------------------
    # Remove impossible values
    # ------------------------------------------

    df = df[
        (df["price"] > 0)
        & (df["sqft_living"] > 0)
        & (df["sqft_lot"] > 0)
        & (df["bedrooms"] >= 0)
        & (df["bathrooms"] >= 0)
        & (df["yr_built"] > 0)
    ]

    rows_after = len(df)

    print(
        f"Rows removed during cleaning: "
        f"{rows_before - rows_after:,}"
    )

    return df

# --------------------------------------------------
# Feature engineering
# --------------------------------------------------

def engineer_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    # Transaction date features.
    df["sale_year"] = (
        df["date"].dt.year
    )

    df["sale_month"] = (
        df["date"].dt.month
    )

    # Age when property was sold.
    df["property_age"] = (
        df["sale_year"]
        - df["yr_built"]
    )

    # Renovation indicator.
    df["was_renovated"] = (
        df["yr_renovated"] > 0
    ).astype(int)

    # Basement indicator.
    df["has_basement"] = (
        df["sqft_basement"] > 0
    ).astype(int)

    # Portion of living area that is basement.
    df["basement_ratio"] = np.where(
        df["sqft_living"] > 0,
        df["sqft_basement"]
        / df["sqft_living"],
        0,
    )

    # Relative lot size.
    df["lot_to_living_ratio"] = np.where(
        df["sqft_living"] > 0,
        df["sqft_lot"]
        / df["sqft_living"],
        0,
    )

    # Useful for analytics only.
    #
    # IMPORTANT:
    # Do NOT use this column when predicting price.
    # It directly contains our target variable.
    df["price_per_sqft"] = (
        df["price"]
        / df["sqft_living"]
    )

    return df


# --------------------------------------------------
# Final validation
# --------------------------------------------------

def validate_engineered_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    # A property cannot have negative age.
    df = df[
        df["property_age"] >= 0
    ]

    # Convert infinite values to missing.
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return df


# --------------------------------------------------
# Summary
# --------------------------------------------------

def print_summary(
    df: pd.DataFrame
) -> None:

    print("\n==============================")
    print(" EstateIQ Data Summary")
    print("==============================")

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        "Date range:",
        df["date"].min().date(),
        "to",
        df["date"].max().date(),
    )

    print(
        f"Median sale price: "
        f"${df['price'].median():,.0f}"
    )

    print(
        f"Median living area: "
        f"{df['sqft_living'].median():,.0f} sqft"
    )

    print(
        f"ZIP codes: "
        f"{df['zipcode'].nunique()}"
    )

    print(
        f"Renovated properties: "
        f"{df['was_renovated'].sum():,}"
    )

    print(
        f"Properties with basement: "
        f"{df['has_basement'].sum():,}"
    )

    print("==============================")


# --------------------------------------------------
# Save
# --------------------------------------------------

def save_data(
    df: pd.DataFrame,
    path: Path
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        path,
        index=False
    )

    print(
        f"\nProcessed dataset saved to:\n{path}"
    )


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def main() -> None:

    print(
        "\nStarting EstateIQ preprocessing...\n"
    )

    df = load_data(
        RAW_DATA_PATH
    )

    validate_columns(df)

    df = clean_data(df)

    df = engineer_features(df)

    df = validate_engineered_data(df)

    # Sort chronologically.
    # We will use this later for our
    # train / validation / test split.
    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    print_summary(df)

    save_data(
        df,
        PROCESSED_DATA_PATH
    )

    print(
        "\nEstateIQ preprocessing completed successfully."
    )


if __name__ == "__main__":
    main()