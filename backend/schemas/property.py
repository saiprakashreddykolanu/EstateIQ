import math

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


# ---------------------------------------------------------
# ESTATEIQ PROPERTY INPUT SCHEMA
# ---------------------------------------------------------

class PropertyInput(BaseModel):

    # -----------------------------------------------------
    # CORE PROPERTY CHARACTERISTICS
    # -----------------------------------------------------

    bedrooms: int = Field(
        ...,
        ge=0,
        le=20,
        description="Number of bedrooms",
    )

    bathrooms: float = Field(
        ...,
        ge=0,
        le=20,
        description="Number of bathrooms",
    )

    sqft_living: int = Field(
        ...,
        gt=0,
        le=20000,
        description="Total living area in square feet",
    )

    sqft_lot: int = Field(
        ...,
        gt=0,
        le=2000000,
        description="Lot size in square feet",
    )

    floors: float = Field(
        ...,
        ge=0.5,
        le=4,
        description=(
            "Number of floors. "
            "Accepted in 0.5-floor increments."
        ),
    )


    # -----------------------------------------------------
    # PROPERTY CHARACTERISTICS
    # -----------------------------------------------------

    waterfront: int = Field(
        ...,
        ge=0,
        le=1,
        description=(
            "Waterfront indicator: "
            "0 = no, 1 = yes"
        ),
    )

    view: int = Field(
        ...,
        ge=0,
        le=4,
        description="Property view quality",
    )

    condition: int = Field(
        ...,
        ge=1,
        le=5,
        description="Property condition score",
    )

    grade: int = Field(
        ...,
        ge=1,
        le=13,
        description="King County property grade",
    )


    # -----------------------------------------------------
    # AREA COMPONENTS
    # -----------------------------------------------------

    sqft_above: int = Field(
        ...,
        gt=0,
        le=20000,
        description=(
            "Above-ground living area "
            "in square feet"
        ),
    )

    sqft_basement: int = Field(
        ...,
        ge=0,
        le=10000,
        description=(
            "Basement living area "
            "in square feet"
        ),
    )


    # -----------------------------------------------------
    # PROPERTY AGE / RENOVATION
    # -----------------------------------------------------

    year_built: int = Field(
        ...,
        ge=1800,
        le=2015,
        description=(
            "Year property was built. "
            "EstateIQ V1 uses the historical "
            "2014-2015 King County market."
        ),
    )

    year_renovated: int = Field(
        ...,
        ge=0,
        le=2015,
        description=(
            "Year renovated. "
            "Use 0 if never renovated."
        ),
    )


    # -----------------------------------------------------
    # LOCATION
    # -----------------------------------------------------

    zipcode: int = Field(
        ...,
        ge=98000,
        le=98200,
        description="King County ZIP code",
    )

    latitude: float = Field(
        ...,
        ge=47.0,
        le=48.0,
        description="Property latitude",
    )

    longitude: float = Field(
        ...,
        ge=-123.0,
        le=-121.0,
        description="Property longitude",
    )


    # -----------------------------------------------------
    # NEIGHBORHOOD CHARACTERISTICS
    # -----------------------------------------------------

    sqft_living15: int = Field(
        ...,
        gt=0,
        le=20000,
        description=(
            "Average nearby living area "
            "used by the historical dataset"
        ),
    )

    sqft_lot15: int = Field(
        ...,
        gt=0,
        le=2000000,
        description=(
            "Average nearby lot size "
            "used by the historical dataset"
        ),
    )


    # -----------------------------------------------------
    # CROSS-FIELD VALIDATION
    # -----------------------------------------------------

    @model_validator(mode="after")
    def validate_property_consistency(self):

        errors = []


        # -------------------------------------------------
        # Floor increment consistency
        #
        # EstateIQ accepts half-floor increments:
        #
        # 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4
        # -------------------------------------------------

        doubled_floors = self.floors * 2

        if not math.isclose(
            doubled_floors,
            round(doubled_floors),
            abs_tol=1e-9,
        ):

            errors.append(
                "Floors must use 0.5 increments. "
                "Accepted values are "
                "0.5, 1, 1.5, 2, 2.5, "
                "3, 3.5, and 4."
            )


        # -------------------------------------------------
        # Living area consistency
        #
        # sqft_living =
        # sqft_above + sqft_basement
        # -------------------------------------------------

        component_total = (
            self.sqft_above
            + self.sqft_basement
        )

        if component_total != self.sqft_living:

            errors.append(
                "Living area is inconsistent: "
                "sqft_living must equal "
                "sqft_above + sqft_basement. "
                f"Received sqft_living="
                f"{self.sqft_living}, "
                f"sqft_above="
                f"{self.sqft_above}, "
                f"sqft_basement="
                f"{self.sqft_basement}."
            )


        # -------------------------------------------------
        # Renovation year consistency
        # -------------------------------------------------

        if (
            self.year_renovated != 0
            and
            self.year_renovated
            < self.year_built
        ):

            errors.append(
                "Renovation year cannot be "
                "earlier than year built. "
                "Use 0 if the property was "
                "never renovated."
            )


        # -------------------------------------------------
        # Above-ground area cannot exceed living area
        # -------------------------------------------------

        if (
            self.sqft_above
            > self.sqft_living
        ):

            errors.append(
                "Above-ground living area cannot "
                "exceed total living area."
            )


        # -------------------------------------------------
        # Basement cannot exceed total living area
        # -------------------------------------------------

        if (
            self.sqft_basement
            > self.sqft_living
        ):

            errors.append(
                "Basement area cannot exceed "
                "total living area."
            )


        # -------------------------------------------------
        # Lot should not be smaller than building footprint
        # -------------------------------------------------

        if (
            self.sqft_lot
            < self.sqft_above / self.floors
        ):

            errors.append(
                "Lot size appears inconsistent "
                "with the approximate building "
                "footprint."
            )


        # -------------------------------------------------
        # Raise validation error
        # -------------------------------------------------

        if errors:

            raise ValueError(
                " ".join(errors)
            )


        return self