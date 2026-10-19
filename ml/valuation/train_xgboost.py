from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from xgboost import XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "properties_clean.csv"
)

ARTIFACT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "artifacts"
)

MODEL_PATH = (
    ARTIFACT_DIR
    / "valuation_xgb_v1.joblib"
)

METADATA_PATH = (
    ARTIFACT_DIR
    / "valuation_xgb_v1_metadata.json"
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

TARGET = "price"


def load_data():

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["date"]
    )

    return (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )


def chronological_split(df):

    n = len(df)

    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train = df.iloc[:train_end]
    validation = df.iloc[
        train_end:val_end
    ]
    test = df.iloc[val_end:]

    return train, validation, test


def evaluate(
    model,
    X,
    y,
    label
):

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
    print("-" * 40)

    print(
        f"MAE:  ${mae:,.2f}"
    )

    print(
        f"RMSE: ${rmse:,.2f}"
    )

    print(
        f"R²:    {r2:.4f}"
    )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }


def main():

    print("\nEstateIQ XGBoost Valuation")
    print("=" * 40)

    df = load_data()

    print(
        f"Loaded {len(df):,} transactions."
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

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_val = val_df[FEATURES]
    y_val = val_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    # ------------------------------------------
    # XGBoost V1
    # ------------------------------------------

    model = XGBRegressor(
        objective="reg:squarederror",

        n_estimators=700,
        learning_rate=0.03,

        max_depth=6,

        min_child_weight=3,

        subsample=0.8,
        colsample_bytree=0.8,

        reg_alpha=0.1,
        reg_lambda=1.0,

        random_state=42,
        n_jobs=-1,
    )

    print(
        "\nTraining XGBoost..."
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[
            (X_val, y_val)
        ],
        verbose=False,
    )

    print(
        "Training complete."
    )

    train_metrics = evaluate(
        model,
        X_train,
        y_train,
        "TRAIN RESULTS"
    )

    validation_metrics = evaluate(
        model,
        X_val,
        y_val,
        "VALIDATION RESULTS"
    )

    test_metrics = evaluate(
        model,
        X_test,
        y_test,
        "TEST RESULTS"
    )

    # ------------------------------------------
    # Save artifacts
    # ------------------------------------------

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    metadata = {
        "model": "XGBRegressor",
        "version": "1.0",
        "target": TARGET,

        "features": FEATURES,

        "training_rows": len(train_df),
        "validation_rows": len(val_df),
        "test_rows": len(test_df),

        "parameters": model.get_params(),

        "metrics": {
            "train": train_metrics,
            "validation": validation_metrics,
            "test": test_metrics,
        },
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print(
        f"\nModel saved to:\n{MODEL_PATH}"
    )

    print(
        f"\nMetadata saved to:\n"
        f"{METADATA_PATH}"
    )

    print(
        "\nEstateIQ XGBoost training complete."
    )


if __name__ == "__main__":
    main()