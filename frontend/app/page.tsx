"use client";

import { useState } from "react";
import type {
  FormEvent,
  ReactNode,
} from "react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { analyzeProperty } from "../lib/api";

import type {
  AnalysisResponse,
  PropertyInput,
  ShapFactor,
} from "../lib/types";


/* =========================================================
   TYPES
========================================================= */

type NumericOption = {
  value: number;
  label?: string;
};


/* =========================================================
   OPTION HELPERS
========================================================= */

function createNumberOptions(
  start: number,
  end: number,
  step: number,
  decimals = 0
): NumericOption[] {
  const values: NumericOption[] = [];

  for (
    let value = start;
    value <= end + 0.0000001;
    value += step
  ) {
    values.push({
      value: Number(
        value.toFixed(decimals)
      ),
    });
  }

  return values;
}


/* =========================================================
   DROPDOWN OPTIONS
========================================================= */

const ZIP_OPTIONS =
  createNumberOptions(
    98000,
    98200,
    1
  );


const BEDROOM_OPTIONS =
  createNumberOptions(
    0,
    20,
    1
  );


const BATHROOM_OPTIONS =
  createNumberOptions(
    0,
    20,
    0.25,
    2
  );


const FLOOR_OPTIONS: NumericOption[] = [
  { value: 0.5, label: "0.5 floor" },
  { value: 1, label: "1 floor" },
  { value: 1.5, label: "1.5 floors" },
  { value: 2, label: "2 floors" },
  { value: 2.5, label: "2.5 floors" },
  { value: 3, label: "3 floors" },
  { value: 3.5, label: "3.5 floors" },
  { value: 4, label: "4 floors" },
];


const WATERFRONT_OPTIONS:
  NumericOption[] = [
  {
    value: 0,
    label: "No waterfront",
  },
  {
    value: 1,
    label: "Waterfront",
  },
];


const VIEW_OPTIONS:
  NumericOption[] = [
  {
    value: 0,
    label: "None",
  },
  {
    value: 1,
    label: "Fair",
  },
  {
    value: 2,
    label: "Average",
  },
  {
    value: 3,
    label: "Good",
  },
  {
    value: 4,
    label: "Excellent",
  },
];


const CONDITION_OPTIONS:
  NumericOption[] = [
  {
    value: 1,
    label: "Poor",
  },
  {
    value: 2,
    label: "Fair",
  },
  {
    value: 3,
    label: "Average",
  },
  {
    value: 4,
    label: "Good",
  },
  {
    value: 5,
    label: "Excellent",
  },
];


const GRADE_OPTIONS =
  createNumberOptions(
    1,
    13,
    1
  );


const YEAR_BUILT_OPTIONS =
  createNumberOptions(
    1800,
    2015,
    1
  );


const YEAR_RENOVATED_OPTIONS:
  NumericOption[] = [
  {
    value: 0,
    label: "Never renovated",
  },
  ...createNumberOptions(
    1800,
    2015,
    1
  ),
];


const LATITUDE_OPTIONS =
  createNumberOptions(
    47,
    48,
    0.05,
    2
  );


const LONGITUDE_OPTIONS =
  createNumberOptions(
    -123,
    -121,
    0.05,
    2
  );


const LIVING_AREA_OPTIONS:
  NumericOption[] = [
  500,
  750,
  1000,
  1250,
  1500,
  1750,
  2000,
  2250,
  2450,
  2500,
  2750,
  3000,
  3200,
  3500,
  4000,
  4500,
  5000,
  6000,
  7500,
  10000,
  12500,
  15000,
  17500,
  20000,
].map((value) => ({
  value,
}));


const BASEMENT_OPTIONS:
  NumericOption[] = [
  0,
  250,
  500,
  750,
  1000,
  1250,
  1500,
  1750,
  2000,
  2500,
  3000,
  4000,
  5000,
  7500,
  10000,
].map((value) => ({
  value,
}));


const LOT_SIZE_OPTIONS:
  NumericOption[] = [
  500,
  1000,
  2000,
  3000,
  4000,
  5000,
  6000,
  7500,
  8000,
  10000,
  12500,
  15000,
  20000,
  25000,
  50000,
  75000,
  100000,
  250000,
  500000,
  1000000,
  1500000,
  2000000,
].map((value) => ({
  value,
}));


/* =========================================================
   DEFAULT PROPERTY
========================================================= */

const DEFAULT_PROPERTY:
  PropertyInput = {
  bedrooms: 4,
  bathrooms: 3,
  sqft_living: 2450,
  sqft_lot: 7500,
  floors: 2,
  waterfront: 0,
  view: 0,
  condition: 3,
  grade: 8,
  sqft_above: 2450,
  sqft_basement: 0,
  year_built: 2005,
  year_renovated: 0,
  zipcode: 98052,
  latitude: 47.67,
  longitude: -122.12,
  sqft_living15: 2400,
  sqft_lot15: 7500,
};


/* =========================================================
   FORMATTERS
========================================================= */

function currency(
  value: number
) {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }
  ).format(value);
}


function signedCurrency(
  value: number
) {
  const formatted =
    currency(
      Math.abs(value)
    );

  if (value > 0) {
    return `+${formatted}`;
  }

  if (value < 0) {
    return `-${formatted}`;
  }

  return formatted;
}


function formatSaleDate(
  dateString: string
) {
  const [
    year,
    month,
    day,
  ] = dateString.split("-");

  if (
    !year ||
    !month ||
    !day
  ) {
    return dateString;
  }

  return `${month}/${day}/${year}`;
}


function formatFeatureValue(
  factor: ShapFactor
) {
  const value =
    factor.feature_value;

  switch (
    factor.feature
  ) {
    case "sqft_living":
    case "sqft_lot":
    case "sqft_above":
    case "sqft_basement":
    case "sqft_living15":
    case "sqft_lot15":
      return `${value.toLocaleString()} sq ft`;

    case "lat":
    case "long":
      return value.toFixed(4);

    case "basement_ratio":
    case "lot_to_living_ratio":
      return value.toFixed(2);

    case "waterfront":
    case "was_renovated":
    case "has_basement":
      return value === 1
        ? "Yes"
        : "No";

    default:
      return value.toLocaleString();
  }
}


/* =========================================================
   HOME
========================================================= */

export default function Home() {
  const [
    form,
    setForm,
  ] =
    useState<PropertyInput>(
      DEFAULT_PROPERTY
    );

  const [
    result,
    setResult,
  ] =
    useState<AnalysisResponse | null>(
      null
    );

  const [
    loading,
    setLoading,
  ] =
    useState(false);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    );


  /* -------------------------------------------------------
     UPDATE FIELD
  ------------------------------------------------------- */

  function updateField(
    field:
      keyof PropertyInput,
    value: string
  ) {
    setForm(
      (current) => ({
        ...current,
        [field]:
          Number(value),
      })
    );
  }


  /* -------------------------------------------------------
     RESET
  ------------------------------------------------------- */

  function resetProperty() {
    setForm(
      DEFAULT_PROPERTY
    );

    setResult(null);
    setError(null);
  }


  /* -------------------------------------------------------
     VALIDATION
  ------------------------------------------------------- */

  function validateForm():
    string | null {

    const doubledFloors =
      form.floors * 2;

    if (
      Math.abs(
        doubledFloors -
          Math.round(
            doubledFloors
          )
      ) > 1e-9
    ) {
      return (
        "Floors must use " +
        "0.5 increments. " +
        "Accepted values are " +
        "0.5, 1, 1.5, 2, " +
        "2.5, 3, 3.5, and 4."
      );
    }


    if (
      form.sqft_living !==
      form.sqft_above +
        form.sqft_basement
    ) {
      return (
        "Living Area must " +
        "equal Above Ground " +
        "+ Basement."
      );
    }


    if (
      form.year_renovated !==
        0 &&
      form.year_renovated <
        form.year_built
    ) {
      return (
        "Year Renovated " +
        "cannot be earlier " +
        "than Year Built. " +
        "Use 0 if never " +
        "renovated."
      );
    }


    if (
      form.sqft_above >
      form.sqft_living
    ) {
      return (
        "Above Ground area " +
        "cannot exceed total " +
        "Living Area."
      );
    }


    if (
      form.sqft_basement >
      form.sqft_living
    ) {
      return (
        "Basement area " +
        "cannot exceed total " +
        "Living Area."
      );
    }


    if (
      form.sqft_lot <
      form.sqft_above /
        form.floors
    ) {
      return (
        "Lot Size appears " +
        "too small for the " +
        "approximate building " +
        "footprint."
      );
    }


    return null;
  }


  /* -------------------------------------------------------
     SUBMIT
  ------------------------------------------------------- */

  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError(null);

    const validationError =
      validateForm();

    if (
      validationError
    ) {
      setError(
        validationError
      );

      return;
    }


    setLoading(true);

    try {
      const analysis =
        await analyzeProperty(
          form
        );

      setResult(
        analysis
      );


      setTimeout(
        () => {
          document
            .getElementById(
              "analysis-results"
            )
            ?.scrollIntoView({
              behavior:
                "smooth",
              block:
                "start",
            });
        },
        100
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : (
            "Unable to " +
            "analyze property."
          )
      );

    } finally {

      setLoading(false);

    }
  }


  /* -------------------------------------------------------
     DERIVED RESULTS
  ------------------------------------------------------- */

  const estimatedValue =
    result?.valuation
      .estimated_value ??
    0;


  const medianComparable =
    result
      ?.comparable_analysis
      .median_comparable_price ??
    0;


  const difference =
    estimatedValue -
    medianComparable;


  const differencePercent =
    medianComparable !== 0
      ? (
          difference /
          medianComparable
        ) * 100
      : 0;


  const chartData =
    result
      ? [
          {
            name:
              "AI Estimate",
            price:
              result
                .valuation
                .estimated_value,
            type:
              "estimate",
          },

          ...result
            .comparable_analysis
            .comparables
            .map(
              (
                property,
                index
              ) => ({
                name:
                  `Comp ${
                    index + 1
                  }`,
                price:
                  property
                    .sale_price,
                type:
                  "comparable",
              })
            ),
        ]
      : [];


  return (
    <main className="min-h-screen bg-[#07111f] text-slate-100">

      {/* ===================================================
          NAVIGATION
      =================================================== */}

      <header className="sticky top-0 z-50 border-b border-white/5 bg-[#07111f]/90 backdrop-blur-xl">

        <div className="mx-auto flex max-w-[1440px] items-center justify-between px-5 py-4 md:px-8">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400 text-sm font-black text-slate-950 shadow-lg shadow-cyan-400/20">
              EI
            </div>


            <div>

              <div className="text-xl font-bold tracking-tight">

                Estate

                <span className="text-cyan-400">
                  IQ
                </span>

              </div>


              <p className="text-[11px] text-slate-500">
                Property Intelligence Platform
              </p>

            </div>

          </div>


          <div className="hidden items-center gap-3 md:flex">

            <StatusPill>
              Historical Model
            </StatusPill>

            <StatusPill>
              King County
            </StatusPill>


            <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs text-emerald-300">

              <span className="h-2 w-2 rounded-full bg-emerald-400" />

              ML Pipeline Ready

            </div>

          </div>

        </div>

      </header>


      {/* ===================================================
          HERO
      =================================================== */}

      <section className="relative overflow-hidden border-b border-white/5">

        <div className="hero-glow" />

        <div className="relative mx-auto max-w-[1440px] px-5 py-16 md:px-8 md:py-24">

          <div className="max-w-4xl">

            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">
              Machine Learning Property Analysis
            </div>


            <h1 className="text-4xl font-bold tracking-[-0.04em] text-white sm:text-5xl lg:text-6xl">

              Property intelligence,

              <span className="block text-gradient">
                explained by data.
              </span>

            </h1>


            <p className="mt-6 max-w-3xl text-base leading-8 text-slate-400 md:text-lg">

              Estimate property value,
              discover comparable sales,
              understand ZIP-level market
              position, and inspect the
              model factors driving each
              prediction.

            </p>


            <div className="mt-8 flex flex-wrap gap-3">

              <ModelBadge
                title="XGBoost"
                detail="Valuation"
              />

              <ModelBadge
                title="KNN"
                detail="Comparables"
              />

              <ModelBadge
                title="K-Means"
                detail="Segmentation"
              />

              <ModelBadge
                title="SHAP"
                detail="Explainability"
              />

            </div>

          </div>

        </div>

      </section>


      <div className="mx-auto max-w-[1440px] px-5 py-10 md:px-8">

        <section className="grid gap-6 xl:grid-cols-[400px_minmax(0,1fr)]">

          {/* =================================================
              INPUT PANEL
          ================================================= */}

          <aside className="h-fit rounded-3xl border border-white/5 bg-slate-900/60 shadow-2xl shadow-black/20 xl:sticky xl:top-24">

            <div className="border-b border-white/5 p-6">

              <div className="flex items-center justify-between gap-4">

                <div>

                  <p className="section-eyebrow">
                    Property Input
                  </p>

                  <h2 className="mt-2 text-xl font-semibold">
                    Analyze Property
                  </h2>

                </div>


                <button
                  type="button"
                  onClick={
                    resetProperty
                  }
                  className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-400 transition hover:border-slate-600 hover:text-white"
                >
                  Reset
                </button>

              </div>


              <p className="mt-3 text-sm leading-6 text-slate-500">

                Choose a suggested
                value from each
                dropdown or type a
                valid value manually.

              </p>

            </div>


            <form
              onSubmit={
                handleSubmit
              }
              className="p-6"
            >

              {/* ===========================================
                  LOCATION
              =========================================== */}

              <FormGroup title="Location">

                <ComboInput
                  id="zipcode"
                  label="ZIP Code"
                  value={
                    form.zipcode
                  }
                  min={98000}
                  max={98200}
                  step="1"
                  range="98000–98200"
                  hint="Choose from the dropdown or type a ZIP manually."
                  options={
                    ZIP_OPTIONS
                  }
                  onChange={(
                    value
                  ) =>
                    updateField(
                      "zipcode",
                      value
                    )
                  }
                />


                <div className="grid grid-cols-2 gap-3">

                  <ComboInput
                    id="latitude"
                    label="Latitude"
                    value={
                      form.latitude
                    }
                    min={47}
                    max={48}
                    step="any"
                    range="47.0–48.0"
                    options={
                      LATITUDE_OPTIONS
                    }
                    hint="Suggestions use 0.05 increments. Manual coordinates are allowed."
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "latitude",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="longitude"
                    label="Longitude"
                    value={
                      form.longitude
                    }
                    min={-123}
                    max={-121}
                    step="any"
                    range="-123.0–-121.0"
                    options={
                      LONGITUDE_OPTIONS
                    }
                    hint="Manual coordinates are allowed within the range."
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "longitude",
                        value
                      )
                    }
                  />

                </div>

              </FormGroup>


              {/* ===========================================
                  PROPERTY SIZE
              =========================================== */}

              <FormGroup title="Property Size">

                <div className="grid grid-cols-2 gap-3">

                  <ComboInput
                    id="bedrooms"
                    label="Bedrooms"
                    value={
                      form.bedrooms
                    }
                    min={0}
                    max={20}
                    step="1"
                    range="0–20"
                    options={
                      BEDROOM_OPTIONS
                    }
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "bedrooms",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="bathrooms"
                    label="Bathrooms"
                    value={
                      form.bathrooms
                    }
                    min={0}
                    max={20}
                    step="any"
                    range="0–20"
                    options={
                      BATHROOM_OPTIONS
                    }
                    hint="Dropdown suggestions use quarter-bath increments."
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "bathrooms",
                        value
                      )
                    }
                  />

                </div>


                <ComboInput
                  id="sqft-living"
                  label="Living Area"
                  suffix="sq ft"
                  value={
                    form.sqft_living
                  }
                  min={1}
                  max={20000}
                  step="1"
                  range="1–20,000"
                  options={
                    LIVING_AREA_OPTIONS
                  }
                  hint="Choose a common size or enter the exact living area."
                  onChange={(
                    value
                  ) =>
                    updateField(
                      "sqft_living",
                      value
                    )
                  }
                />


                <ComboInput
                  id="sqft-lot"
                  label="Lot Size"
                  suffix="sq ft"
                  value={
                    form.sqft_lot
                  }
                  min={1}
                  max={2000000}
                  step="1"
                  range="1–2,000,000"
                  options={
                    LOT_SIZE_OPTIONS
                  }
                  hint="Dropdown contains common lot sizes. Exact values can be typed manually."
                  onChange={(
                    value
                  ) =>
                    updateField(
                      "sqft_lot",
                      value
                    )
                  }
                />


                <div className="grid grid-cols-2 gap-3">

                  <ComboInput
                    id="sqft-above"
                    label="Above Ground"
                    suffix="sq ft"
                    value={
                      form.sqft_above
                    }
                    min={1}
                    max={20000}
                    step="1"
                    range="1–20,000"
                    options={
                      LIVING_AREA_OPTIONS
                    }
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "sqft_above",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="sqft-basement"
                    label="Basement"
                    suffix="sq ft"
                    value={
                      form.sqft_basement
                    }
                    min={0}
                    max={10000}
                    step="1"
                    range="0–10,000"
                    options={
                      BASEMENT_OPTIONS
                    }
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "sqft_basement",
                        value
                      )
                    }
                  />

                </div>


                <InfoBox>
                  Living Area =
                  Above Ground +
                  Basement.
                </InfoBox>

              </FormGroup>


              {/* ===========================================
                  PROPERTY PROFILE
              =========================================== */}

              <FormGroup title="Property Profile">

                <div className="grid grid-cols-2 gap-3">

                  <ComboInput
                    id="floors"
                    label="Floors"
                    value={
                      form.floors
                    }
                    min={0.5}
                    max={4}
                    step="0.5"
                    range="0.5–4"
                    options={
                      FLOOR_OPTIONS
                    }
                    hint="Manual values must use 0.5-floor increments."
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "floors",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="year-built"
                    label="Year Built"
                    value={
                      form.year_built
                    }
                    min={1800}
                    max={2015}
                    step="1"
                    range="1800–2015"
                    options={
                      YEAR_BUILT_OPTIONS
                    }
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "year_built",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="grade"
                    label="Grade"
                    value={
                      form.grade
                    }
                    min={1}
                    max={13}
                    step="1"
                    range="1–13"
                    options={
                      GRADE_OPTIONS
                    }
                    hint="King County property grade."
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "grade",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="condition"
                    label="Condition"
                    value={
                      form.condition
                    }
                    min={1}
                    max={5}
                    step="1"
                    range="1–5"
                    options={
                      CONDITION_OPTIONS
                    }
                    hint="1 = poor · 3 = average · 5 = excellent"
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "condition",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="waterfront"
                    label="Waterfront"
                    value={
                      form.waterfront
                    }
                    min={0}
                    max={1}
                    step="1"
                    range="0–1"
                    options={
                      WATERFRONT_OPTIONS
                    }
                    hint="0 = No · 1 = Yes"
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "waterfront",
                        value
                      )
                    }
                  />


                  <ComboInput
                    id="view"
                    label="View"
                    value={
                      form.view
                    }
                    min={0}
                    max={4}
                    step="1"
                    range="0–4"
                    options={
                      VIEW_OPTIONS
                    }
                    onChange={(
                      value
                    ) =>
                      updateField(
                        "view",
                        value
                      )
                    }
                  />

                </div>


                <ComboInput
                  id="year-renovated"
                  label="Year Renovated"
                  value={
                    form.year_renovated
                  }
                  min={0}
                  max={2015}
                  step="1"
                  range="0 or ≤2015"
                  options={
                    YEAR_RENOVATED_OPTIONS
                  }
                  hint="0 = never renovated. A non-zero year cannot be earlier than Year Built."
                  onChange={(
                    value
                  ) =>
                    updateField(
                      "year_renovated",
                      value
                    )
                  }
                />

              </FormGroup>


              {/* ===========================================
                  NEIGHBORHOOD
              =========================================== */}

              <FormGroup
                title="Neighborhood Context"
                last
              >

                <ComboInput
                  id="living-15"
                  label="Nearby Living Area"
                  suffix="sq ft"
                  value={
                    form.sqft_living15
                  }
                  min={1}
                  max={20000}
                  step="1"
                  range="1–20,000"
                  options={
                    LIVING_AREA_OPTIONS
                  }
                  hint="Choose a typical size or enter the exact historical neighborhood value."
                  onChange={(
                    value
                  ) =>
                    updateField(
                      "sqft_living15",
                      value
                    )
                  }
                />


                <ComboInput
                  id="lot-15"
                  label="Nearby Lot Size"
                  suffix="sq ft"
                  value={
                    form.sqft_lot15
                  }
                  min={1}
                  max={2000000}
                  step="1"
                  range="1–2,000,000"
                  options={
                    LOT_SIZE_OPTIONS
                  }
                  hint="Choose a common size or enter the exact value manually."
                  onChange={(
                    value
                  ) =>
                    updateField(
                      "sqft_lot15",
                      value
                    )
                  }
                />

              </FormGroup>


              {error && (
                <div className="mb-4 rounded-xl border border-rose-400/20 bg-rose-400/5 p-4 text-sm leading-6 text-rose-300">
                  {error}
                </div>
              )}


              <button
                type="submit"
                disabled={
                  loading
                }
                className="group relative w-full overflow-hidden rounded-xl bg-cyan-400 px-5 py-3.5 font-semibold text-slate-950 shadow-lg shadow-cyan-400/10 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              >

                <span className="relative z-10">

                  {loading
                    ? (
                      "Running ML Pipeline..."
                    )
                    : (
                      "Run Property Analysis"
                    )}

                </span>

              </button>


              <p className="mt-3 text-center text-[11px] leading-5 text-slate-600">

                Historical King
                County model ·
                2014–2015
                transactions

              </p>

            </form>

          </aside>


          {/* =================================================
              DASHBOARD
          ================================================= */}

          <div className="min-w-0">

            {!result &&
              !loading && (
                <EmptyDashboard />
              )}


            {loading && (
              <LoadingDashboard />
            )}


            {result &&
              !loading && (

              <div
                id="analysis-results"
                className="scroll-mt-28"
              >

                <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">

                  <div>

                    <p className="section-eyebrow">
                      Analysis Overview
                    </p>


                    <h2 className="mt-2 text-2xl font-semibold tracking-tight md:text-3xl">

                      ZIP{" "}
                      {
                        result
                          .property
                          .zipcode
                      }{" "}
                      Property
                      Intelligence

                    </h2>


                    <p className="mt-2 text-sm text-slate-500">

                      {
                        result
                          .property
                          .bedrooms
                      }{" "}
                      bedrooms ·{" "}

                      {
                        result
                          .property
                          .bathrooms
                      }{" "}
                      bathrooms ·{" "}

                      {result.property.sqft_living.toLocaleString()}{" "}
                      sq ft · Built{" "}

                      {
                        result
                          .property
                          .year_built
                      }

                    </p>

                  </div>


                  <div className="flex items-center gap-2 text-xs text-slate-500">

                    <span className="h-2 w-2 rounded-full bg-emerald-400" />

                    Analysis complete

                  </div>

                </div>


                {/* =========================================
                    PRIMARY KPIs
                ========================================= */}

                <section className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">

                  <PrimaryMetric
                    label="Estimated Value"
                    value={
                      currency(
                        result
                          .valuation
                          .estimated_value
                      )
                    }
                    detail="XGBoost model estimate"
                    accent
                  />


                  <PrimaryMetric
                    label="Comparable Median"
                    value={
                      currency(
                        result
                          .comparable_analysis
                          .median_comparable_price
                      )
                    }
                    detail="Median of top 5 KNN matches"
                  />


                  <PrimaryMetric
                    label="Market Segment"
                    value={
                      result
                        .market_analysis
                        .available
                        ? (
                          result
                            .market_analysis
                            .segment ??
                          "Unknown"
                        )
                        : "Unavailable"
                    }
                    detail="K-Means ZIP classification"
                  />


                  <PrimaryMetric
                    label="Vs. Comparable Median"
                    value={`${differencePercent >= 0 ? "+" : ""}${differencePercent.toFixed(1)}%`}
                    detail={
                      signedCurrency(
                        difference
                      )
                    }
                    trend={
                      difference >= 0
                        ? "positive"
                        : "negative"
                    }
                  />

                </section>


                <section className="mt-4 grid gap-px overflow-hidden rounded-2xl border border-white/5 bg-white/5 sm:grid-cols-3">

                  <CompactMetric
                    label="Model Test R²"
                    value="0.8812"
                    detail="XGBoost holdout"
                  />

                  <CompactMetric
                    label="Test MAE"
                    value="$76,422"
                    detail="Valuation error"
                  />

                  <CompactMetric
                    label="Comparable Strategy"
                    value="Same ZIP"
                    detail="KNN candidate pool"
                  />

                </section>


                {/* =========================================
                    SHAP
                ========================================= */}

                {result
                  .valuation_explanation
                  ?.available && (

                  <ShapExplanation
                    explanation={
                      result
                        .valuation_explanation
                    }
                  />

                )}


                {/* =========================================
                    MARKET + CHART
                ========================================= */}

                <section className="mt-6 grid gap-6 2xl:grid-cols-[0.9fr_1.1fr]">

                  {result
                    .market_analysis
                    .available && (

                    <MarketIntelligence
                      result={
                        result
                      }
                    />

                  )}


                  <PriceComparison
                    chartData={
                      chartData
                    }
                  />

                </section>


                {/* =========================================
                    COMPARABLES
                ========================================= */}

                <ComparableSales
                  result={
                    result
                  }
                />


                {/* =========================================
                    MODEL STACK
                ========================================= */}

                <section className="mt-6">

                  <SectionHeader
                    eyebrow="Model Architecture"
                    title="EstateIQ Intelligence Stack"
                    description="Three machine-learning algorithms plus SHAP explainability work together to produce the property intelligence report."
                  />


                  <div className="mt-5 grid gap-4 md:grid-cols-2 2xl:grid-cols-4">

                    <AlgorithmCard
                      number="01"
                      title="XGBoost"
                      subtitle="Property Valuation"
                      description="Gradient-boosted trees estimate property value from structural, geographic, quality, and neighborhood features."
                      metric="Test R²"
                      value="0.8812"
                    />


                    <AlgorithmCard
                      number="02"
                      title="KNN"
                      subtitle="Comparable Sales"
                      description="Standardized property characteristics identify nearby historical transactions within the same ZIP code."
                      metric="Comparables"
                      value={
                        result
                          .comparable_analysis
                          .comparables
                          .length
                          .toString()
                      }
                    />


                    <AlgorithmCard
                      number="03"
                      title="K-Means"
                      subtitle="Market Segmentation"
                      description="ZIP-level housing characteristics identify distinct historical real-estate market segments."
                      metric="Silhouette"
                      value={
                        result
                          .market_analysis
                          .silhouette_score
                          ?.toFixed(4) ??
                        "—"
                      }
                    />


                    <AlgorithmCard
                      number="04"
                      title="SHAP"
                      subtitle="Model Explainability"
                      description="TreeExplainer decomposes the XGBoost prediction into local feature contributions. SHAP is an explainability component rather than a fourth prediction algorithm."
                      metric="Explanation"
                      value="Local"
                    />

                  </div>

                </section>


                <div className="mt-6 rounded-2xl border border-amber-400/10 bg-amber-400/[0.03] p-5">

                  <p className="text-sm font-medium text-amber-200/90">
                    Historical model disclaimer
                  </p>


                  <p className="mt-2 text-sm leading-6 text-amber-100/50">

                    EstateIQ V1 uses
                    historical King
                    County transactions
                    from 2014–2015.
                    Results demonstrate
                    machine-learning
                    techniques and are
                    not current property
                    appraisals.

                  </p>

                </div>

              </div>

            )}

          </div>

        </section>

      </div>


      <footer className="mt-14 border-t border-white/5">

        <div className="mx-auto flex max-w-[1440px] flex-col justify-between gap-3 px-5 py-8 text-xs text-slate-600 md:flex-row md:px-8">

          <p>
            EstateIQ · Machine
            Learning Real Estate
            Intelligence
          </p>

          <p>
            XGBoost · KNN ·
            K-Means · SHAP
          </p>

        </div>

      </footer>

    </main>
  );
}


/* =========================================================
   COMBO INPUT

   INPUT + DATALIST:
   - User can choose from dropdown
   - User can also type manually
========================================================= */

function ComboInput({
  id,
  label,
  value,
  onChange,
  options,
  min,
  max,
  step = "1",
  suffix,
  range,
  hint,
}: {
  id: string;
  label: string;
  value: number;
  onChange:
    (value: string) => void;
  options:
    NumericOption[];
  min?: number;
  max?: number;
  step?: string;
  suffix?: string;
  range?: string;
  hint?: string;
}) {
  const listId =
    `${id}-options`;

  return (
    <label className="block">

      <div className="mb-1.5 flex items-center justify-between gap-2">

        <span className="text-xs font-medium text-slate-400">
          {label}
        </span>


        {range && (
          <span className="text-[10px] font-medium text-cyan-400/70">
            {range}
          </span>
        )}

      </div>


      <div className="relative">

        <input
          id={id}
          type="number"
          list={listId}
          value={value}
          min={min}
          max={max}
          step={step}
          required
          onChange={(
            event
          ) =>
            onChange(
              event.target.value
            )
          }
          className={`w-full rounded-xl border border-slate-800 bg-[#08121f] px-3 py-2.5 text-sm text-slate-100 outline-none transition hover:border-slate-700 focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-400/10 ${
            suffix
              ? "pr-16"
              : ""
          }`}
        />


        <datalist
          id={listId}
        >
          {options.map(
            (
              option,
              index
            ) => (

            <option
              key={`${id}-${option.value}-${index}`}
              value={
                option.value
              }
              label={
                option.label
              }
            />

          ))}
        </datalist>


        {suffix && (
          <span className="pointer-events-none absolute right-8 top-1/2 -translate-y-1/2 text-[10px] text-slate-600">
            {suffix}
          </span>
        )}

      </div>


      {hint && (
        <p className="mt-1.5 text-[10px] leading-4 text-slate-600">
          {hint}
        </p>
      )}

    </label>
  );
}


/* =========================================================
   FORM GROUP
========================================================= */

function FormGroup({
  title,
  children,
  last = false,
}: {
  title: string;
  children: ReactNode;
  last?: boolean;
}) {
  return (
    <div
      className={
        last
          ? "mb-5"
          : "mb-6 border-b border-white/5 pb-6"
      }
    >

      <p className="mb-4 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-600">
        {title}
      </p>

      <div className="space-y-3">
        {children}
      </div>

    </div>
  );
}


function InfoBox({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="rounded-lg border border-cyan-400/10 bg-cyan-400/[0.03] px-3 py-2 text-[10px] leading-4 text-slate-500">
      {children}
    </div>
  );
}


/* =========================================================
   EMPTY DASHBOARD
========================================================= */

function EmptyDashboard() {
  return (
    <div className="flex min-h-[720px] items-center justify-center rounded-3xl border border-dashed border-slate-800 bg-slate-900/20 p-8">

      <div className="max-w-lg text-center">

        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/5 text-xl font-bold text-cyan-300">
          AI
        </div>


        <h2 className="mt-6 text-2xl font-semibold">
          Property intelligence
          starts here
        </h2>


        <p className="mt-3 text-sm leading-7 text-slate-500">

          Choose suggested
          property values or
          enter valid values
          manually, then run the
          EstateIQ pipeline.

        </p>


        <div className="mt-8 grid grid-cols-2 gap-3 text-left">

          <EmptyFeature
            number="01"
            title="Valuation"
            detail="XGBoost"
          />

          <EmptyFeature
            number="02"
            title="Comparables"
            detail="KNN"
          />

          <EmptyFeature
            number="03"
            title="Market"
            detail="K-Means"
          />

          <EmptyFeature
            number="04"
            title="Explanation"
            detail="SHAP"
          />

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   LOADING
========================================================= */

function LoadingDashboard() {
  return (
    <div className="space-y-5">

      <div className="rounded-3xl border border-cyan-400/10 bg-cyan-400/[0.03] p-6">

        <div className="flex items-center gap-4">

          <div className="h-10 w-10 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />

          <div>

            <p className="font-semibold">
              Running EstateIQ
              analysis
            </p>

            <p className="mt-1 text-sm text-slate-500">
              XGBoost, KNN,
              K-Means, and SHAP
              are processing this
              property.
            </p>

          </div>

        </div>

      </div>


      <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">

        {[1, 2, 3, 4].map(
          (item) => (

          <div
            key={item}
            className="h-36 animate-pulse rounded-2xl border border-white/5 bg-slate-900/50"
          />

        ))}

      </div>


      <div className="h-96 animate-pulse rounded-3xl border border-white/5 bg-slate-900/50" />

    </div>
  );
}


/* =========================================================
   SHAP
========================================================= */

function ShapExplanation({
  explanation,
}: {
  explanation:
    AnalysisResponse[
      "valuation_explanation"
    ];
}) {
  const maxImpact =
    Math.max(
      ...explanation
        .top_factors
        .map(
          (factor) =>
            factor
              .absolute_impact
        ),
      1
    );


  const reconstructionDifference =
    explanation
      .predicted_value -
    explanation
      .reconstructed_prediction;


  return (
    <section className="mt-6 overflow-hidden rounded-3xl border border-white/5 bg-slate-900/60">

      <div className="border-b border-white/5 p-6 md:p-7">

        <p className="section-eyebrow">
          Explainable AI · SHAP
        </p>

        <h2 className="mt-2 text-2xl font-semibold">
          Why this valuation?
        </h2>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">

          SHAP decomposes the
          individual XGBoost
          prediction into
          feature-level
          contributions relative
          to the model baseline.

        </p>

      </div>


      <div className="grid gap-px border-b border-white/5 bg-white/5 md:grid-cols-3">

        <ExplanationMetric
          label="Model Baseline"
          value={
            currency(
              explanation
                .base_value
            )
          }
          detail="Expected model output"
        />


        <ExplanationMetric
          label="Net Feature Impact"
          value={
            signedCurrency(
              explanation
                .total_feature_impact
            )
          }
          detail="Combined SHAP contribution"
        />


        <ExplanationMetric
          label="Reconstructed Value"
          value={
            currency(
              explanation
                .reconstructed_prediction
            )
          }
          detail={`Difference ${currency(
            Math.abs(
              reconstructionDifference
            )
          )}`}
        />

      </div>


      <div className="p-6 md:p-7">

        <h3 className="text-lg font-semibold">
          Top Prediction Drivers
        </h3>


        <div className="mt-5 space-y-3">

          {explanation
            .top_factors
            .map(
              (
                factor,
                index
              ) => {

              const width =
                Math.max(
                  (
                    factor
                      .absolute_impact /
                    maxImpact
                  ) * 50,
                  2
                );


              const positive =
                factor.impact >= 0;


              return (
                <div
                  key={
                    factor.feature
                  }
                  className="rounded-2xl border border-white/5 bg-[#091421] p-4"
                >

                  <div className="grid gap-3 lg:grid-cols-[230px_minmax(0,1fr)_130px] lg:items-center">

                    <div>

                      <p className="text-sm font-medium text-slate-200">

                        {String(
                          index + 1
                        ).padStart(
                          2,
                          "0"
                        )}{" "}

                        {
                          factor
                            .display_name
                        }

                      </p>

                      <p className="mt-1 text-xs text-slate-600">

                        {formatFeatureValue(
                          factor
                        )}

                      </p>

                    </div>


                    <div className="relative h-7">

                      <div className="absolute left-1/2 top-0 h-full w-px bg-slate-700" />

                      <div className="absolute inset-y-[10px] left-0 right-0 rounded-full bg-slate-800/70" />


                      {positive ? (

                        <div
                          className="absolute left-1/2 top-[10px] h-[7px] rounded-r-full bg-emerald-400"
                          style={{
                            width:
                              `${width}%`,
                          }}
                        />

                      ) : (

                        <div
                          className="absolute right-1/2 top-[10px] h-[7px] rounded-l-full bg-rose-400"
                          style={{
                            width:
                              `${width}%`,
                          }}
                        />

                      )}

                    </div>


                    <p
                      className={
                        positive
                          ? "font-semibold text-emerald-300 lg:text-right"
                          : "font-semibold text-rose-300 lg:text-right"
                      }
                    >
                      {signedCurrency(
                        factor.impact
                      )}
                    </p>

                  </div>

                </div>
              );
            }
          )}

        </div>

      </div>

    </section>
  );
}


/* =========================================================
   MARKET
========================================================= */

function MarketIntelligence({
  result,
}: {
  result: AnalysisResponse;
}) {
  const market =
    result.market_analysis;


  return (
    <section className="rounded-3xl border border-white/5 bg-slate-900/60 p-6 md:p-7">

      <p className="section-eyebrow">
        K-Means Market Intelligence
      </p>


      <h2 className="mt-3 text-2xl font-semibold">
        {market.segment}
      </h2>


      <p className="mt-2 text-sm text-slate-500">

        ZIP {market.zipcode} ·
        Cluster{" "}
        {market.cluster}

      </p>


      <div className="mt-6 grid grid-cols-2 gap-3">

        <MarketMetric
          label="Historical Sales"
          value={
            market
              .property_count
              ?.toLocaleString() ??
            "—"
          }
        />


        <MarketMetric
          label="ZIP Median"
          value={
            market.median_price !==
              undefined
              ? currency(
                  market.median_price
                )
              : "—"
          }
        />


        <MarketMetric
          label="Price / Sq Ft"
          value={
            market
              .median_price_per_sqft !==
              undefined
              ? `$${market.median_price_per_sqft.toFixed(2)}`
              : "—"
          }
        />


        <MarketMetric
          label="Silhouette"
          value={
            market
              .silhouette_score
              ?.toFixed(4) ??
            "—"
          }
        />

      </div>

    </section>
  );
}


/* =========================================================
   PRICE COMPARISON
========================================================= */

function PriceComparison({
  chartData,
}: {
  chartData: {
    name: string;
    price: number;
    type: string;
  }[];
}) {
  return (
    <section className="rounded-3xl border border-white/5 bg-slate-900/60 p-6 md:p-7">

      <SectionHeader
        eyebrow="Price Position"
        title="Valuation vs. Comparable Sales"
        description="EstateIQ's XGBoost estimate compared with the five nearest historical KNN matches."
      />


      <div className="mt-7 h-[330px] w-full">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <BarChart
            data={chartData}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#1e293b"
            />


            <XAxis
              dataKey="name"
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
              fontSize={12}
            />


            <YAxis
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
              width={70}
              tickFormatter={(
                value
              ) =>
                `$${Math.round(
                  value / 1000
                )}K`
              }
            />


            <Tooltip
              formatter={(
                value
              ) => [
                currency(
                  Number(value)
                ),
                "Price",
              ]}
            />


            <Bar
              dataKey="price"
              radius={[
                7,
                7,
                0,
                0,
              ]}
            >

              {chartData.map(
                (
                  entry,
                  index
                ) => (

                <Cell
                  key={
                    `${entry.name}-${index}`
                  }
                  fill={
                    entry.type ===
                      "estimate"
                      ? "#22d3ee"
                      : "#475569"
                  }
                />

              ))}

            </Bar>

          </BarChart>

        </ResponsiveContainer>

      </div>

    </section>
  );
}


/* =========================================================
   COMPARABLE SALES
========================================================= */

function ComparableSales({
  result,
}: {
  result: AnalysisResponse;
}) {
  return (
    <section className="mt-6 overflow-hidden rounded-3xl border border-white/5 bg-slate-900/60">

      <div className="border-b border-white/5 p-6">

        <SectionHeader
          eyebrow="KNN Comparable Analysis"
          title="Comparable Sales"
          description={`Nearest historical property matches from ZIP ${result.property.zipcode}.`}
        />

      </div>


      <div className="overflow-x-auto">

        <table className="w-full min-w-[850px] text-left text-sm">

          <thead>

            <tr className="border-b border-white/5 text-xs text-slate-600">

              <th className="px-6 py-4">
                Rank
              </th>

              <th className="px-6 py-4">
                Sale Price
              </th>

              <th className="px-6 py-4">
                Sale Date
              </th>

              <th className="px-6 py-4">
                Living Area
              </th>

              <th className="px-6 py-4">
                Beds / Baths
              </th>

              <th className="px-6 py-4">
                Grade
              </th>

              <th className="px-6 py-4">
                Similarity
              </th>

            </tr>

          </thead>


          <tbody>

            {result
              .comparable_analysis
              .comparables
              .map(
                (
                  property,
                  index
                ) => (

                <tr
                  key={
                    property
                      .property_id
                  }
                  className="border-b border-white/5"
                >

                  <td className="px-6 py-5 text-slate-600">
                    #{index + 1}
                  </td>

                  <td className="px-6 py-5 font-semibold">
                    {currency(
                      property
                        .sale_price
                    )}
                  </td>

                  <td className="px-6 py-5 text-slate-400">
                    {formatSaleDate(
                      property
                        .sale_date
                    )}
                  </td>

                  <td className="px-6 py-5 text-slate-400">
                    {property.sqft_living.toLocaleString()}{" "}
                    sq ft
                  </td>

                  <td className="px-6 py-5 text-slate-400">
                    {property.bedrooms}{" "}
                    /{" "}
                    {property.bathrooms}
                  </td>

                  <td className="px-6 py-5 text-slate-400">
                    {property.grade}
                  </td>

                  <td className="px-6 py-5 text-cyan-300">

                    {property
                      .similarity_score
                      .toFixed(1)}
                    %

                  </td>

                </tr>

              ))}

          </tbody>

        </table>

      </div>

    </section>
  );
}


/* =========================================================
   METRICS
========================================================= */

function PrimaryMetric({
  label,
  value,
  detail,
  accent = false,
  trend,
}: {
  label: string;
  value: string;
  detail: string;
  accent?: boolean;
  trend?:
    | "positive"
    | "negative";
}) {
  let valueClass =
    "text-slate-100";

  if (accent) {
    valueClass =
      "text-cyan-300";
  }

  if (
    trend === "positive"
  ) {
    valueClass =
      "text-emerald-300";
  }

  if (
    trend === "negative"
  ) {
    valueClass =
      "text-rose-300";
  }


  return (
    <div className="rounded-2xl border border-white/5 bg-slate-900/60 p-5">

      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p
        className={`mt-3 text-2xl font-bold ${valueClass}`}
      >
        {value}
      </p>

      <p className="mt-2 text-xs text-slate-600">
        {detail}
      </p>

    </div>
  );
}


function CompactMetric({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="bg-slate-900/60 p-4">

      <p className="text-[10px] uppercase text-slate-600">
        {label}
      </p>

      <p className="mt-2 font-semibold">
        {value}
      </p>

      <p className="mt-1 text-[11px] text-slate-600">
        {detail}
      </p>

    </div>
  );
}


function ExplanationMetric({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="bg-slate-900/60 p-5">

      <p className="text-[10px] uppercase text-slate-600">
        {label}
      </p>

      <p className="mt-2 text-xl font-semibold">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-600">
        {detail}
      </p>

    </div>
  );
}


function MarketMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-slate-950/40 p-4">

      <p className="text-[10px] uppercase text-slate-600">
        {label}
      </p>

      <p className="mt-2 font-semibold">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   MODEL CARD
========================================================= */

function AlgorithmCard({
  number,
  title,
  subtitle,
  description,
  metric,
  value,
}: {
  number: string;
  title: string;
  subtitle: string;
  description: string;
  metric: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-white/5 bg-slate-900/60 p-5">

      <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
        Component {number}
      </p>

      <h3 className="mt-2 text-lg font-semibold">
        {title}
      </h3>

      <p className="text-xs text-slate-600">
        {subtitle}
      </p>

      <p className="mt-4 text-sm leading-6 text-slate-500">
        {description}
      </p>

      <div className="mt-4 border-t border-white/5 pt-4">

        <p className="text-[10px] uppercase text-slate-600">
          {metric}
        </p>

        <p className="mt-1 font-semibold">
          {value}
        </p>

      </div>

    </div>
  );
}


/* =========================================================
   SMALL COMPONENTS
========================================================= */

function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div>

      <p className="section-eyebrow">
        {eyebrow}
      </p>

      <h2 className="mt-2 text-xl font-semibold">
        {title}
      </h2>

      <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-500">
        {description}
      </p>

    </div>
  );
}


function StatusPill({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <span className="rounded-full border border-white/5 bg-white/[0.02] px-3 py-1.5 text-xs text-slate-500">
      {children}
    </span>
  );
}


function ModelBadge({
  title,
  detail,
}: {
  title: string;
  detail: string;
}) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-white/5 bg-white/[0.025] px-3 py-2">

      <span className="text-xs font-semibold text-slate-300">
        {title}
      </span>

      <span className="h-1 w-1 rounded-full bg-slate-600" />

      <span className="text-xs text-slate-600">
        {detail}
      </span>

    </div>
  );
}


function EmptyFeature({
  number,
  title,
  detail,
}: {
  number: string;
  title: string;
  detail: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-slate-950/30 p-4">

      <p className="text-[10px] font-semibold text-cyan-400">
        {number}
      </p>

      <p className="mt-2 text-sm font-medium text-slate-300">
        {title}
      </p>

      <p className="mt-1 text-xs text-slate-600">
        {detail}
      </p>

    </div>
  );
}