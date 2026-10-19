from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "properties_clean.csv"
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
    "basement_ratio",
    "lot_to_living_ratio",
    "waterfront_missing",
"view_missing",
"renovation_value_missing",
]

TARGET = "price"


def load_data():
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df


def chronological_split(df):
    """
    Split chronologically:

    First 70%  -> training
    Next 15%   -> validation
    Final 15%  -> testing
    """

    n = len(df)

    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]

    return train_df, val_df, test_df


def evaluate_model(model, X, y, label):
    predictions = model.predict(X)

    mae = mean_absolute_error(
        y,
        predictions
    )

    rmse = mean_squared_error(
        y,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y,
        predictions
    )

    print(f"\n{label}")
    print("-" * 35)
    print(f"MAE:  ${mae:,.2f}")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"R²:    {r2:.4f}")

    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


def main():

    print("\nEstateIQ Baseline Model")
    print("=" * 40)

    df = load_data()

    print(
        f"Loaded {len(df):,} cleaned transactions."
    )

    train_df, val_df, test_df = (
        chronological_split(df)
    )

    print("\nChronological split:")
    print(
        f"Training:   {len(train_df):,}"
    )
    print(
        f"Validation: {len(val_df):,}"
    )
    print(
        f"Testing:    {len(test_df):,}"
    )

    print("\nDate ranges:")

    print(
        "Train:",
        train_df["date"].min().date(),
        "to",
        train_df["date"].max().date(),
    )

    print(
        "Validation:",
        val_df["date"].min().date(),
        "to",
        val_df["date"].max().date(),
    )

    print(
        "Test:",
        test_df["date"].min().date(),
        "to",
        test_df["date"].max().date(),
    )

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_val = val_df[FEATURES]
    y_val = val_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    # Check for unexpected missing values.
    if X_train.isna().any().any():
        raise ValueError(
            "Training features contain missing values."
        )

    model = LinearRegression()

    print("\nTraining Linear Regression...")

    model.fit(
        X_train,
        y_train
    )

    print("Training complete.")

    evaluate_model(
        model,
        X_train,
        y_train,
        "TRAIN RESULTS"
    )

    evaluate_model(
        model,
        X_val,
        y_val,
        "VALIDATION RESULTS"
    )

    evaluate_model(
        model,
        X_test,
        y_test,
        "TEST RESULTS"
    )

    print(
        "\nBaseline evaluation complete."
    )


if __name__ == "__main__":
    main()