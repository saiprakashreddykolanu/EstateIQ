import type {
  AnalysisResponse,
  PropertyInput,
} from "./types";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";


export async function analyzeProperty(
  property: PropertyInput
): Promise<AnalysisResponse> {

  const response = await fetch(
    `${API_URL}/api/v1/analyze`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body:
        JSON.stringify(property),
    }
  );


  if (!response.ok) {

    const errorText =
      await response.text();

    throw new Error(
      `EstateIQ analysis failed: ${errorText}`
    );

  }


  return response.json();
}