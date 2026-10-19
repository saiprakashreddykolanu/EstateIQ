export interface PropertyInput {
  bedrooms: number;
  bathrooms: number;
  sqft_living: number;
  sqft_lot: number;
  floors: number;
  waterfront: number;
  view: number;
  condition: number;
  grade: number;
  sqft_above: number;
  sqft_basement: number;
  year_built: number;
  year_renovated: number;
  zipcode: number;
  latitude: number;
  longitude: number;
  sqft_living15: number;
  sqft_lot15: number;
}

export interface ComparableProperty {
  property_id: number;
  sale_date: string;
  sale_price: number;
  zipcode: number;
  bedrooms: number;
  bathrooms: number;
  sqft_living: number;
  sqft_lot: number;
  year_built: number;
  grade: number;
  condition: number;
  latitude: number;
  longitude: number;
  knn_distance: number;
  similarity_score: number;
}

export interface MarketAnalysis {
  available: boolean;
  zipcode: number;
  segment?: string;
  cluster?: number;
  property_count?: number;
  median_price?: number;
  median_price_per_sqft?: number;
  median_sqft_living?: number;
  median_grade?: number;
  algorithm?: string;
  model_version?: string;
  silhouette_score?: number;
  market_reference?: string;
  message?: string;
}

export interface ShapFactor {
  feature: string;
  display_name: string;
  feature_value: number;
  impact: number;
  absolute_impact: number;
  direction: "increases" | "decreases" | "neutral";
}

export interface ValuationExplanation {
  available: boolean;
  method: string;
  model: string;
  model_version: string;
  base_value: number;
  total_feature_impact: number;
  predicted_value: number;
  reconstructed_prediction: number;
  top_factors: ShapFactor[];
  interpretation: string;
}

export interface AnalysisResponse {
  property: {
    zipcode: number;
    bedrooms: number;
    bathrooms: number;
    sqft_living: number;
    year_built: number;
  };

  valuation: {
    estimated_value: number;
    currency: string;
    algorithm: string;
    model_version: string;
    market_reference: string;
  };

  valuation_explanation: ValuationExplanation;

  comparable_analysis: {
    algorithm: string;
    candidate_strategy: string;
    median_comparable_price: number;
    comparables: ComparableProperty[];
  };

  market_analysis: MarketAnalysis;
}