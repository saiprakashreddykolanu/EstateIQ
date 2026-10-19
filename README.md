\# EstateIQ



EstateIQ is a full-stack machine learning real estate intelligence platform that combines property valuation, comparable sales analysis, market segmentation, and explainable AI.



\## Features



\- XGBoost property valuation

\- K-Nearest Neighbors comparable property analysis

\- K-Means ZIP-level market segmentation

\- SHAP model explainability

\- FastAPI backend

\- Next.js + TypeScript frontend

\- Input validation with Pydantic

\- Automated API tests



\## Machine Learning



\### XGBoost Valuation



EstateIQ uses an XGBoost regression model trained on historical King County housing transactions.



Test performance:



\- MAE: $76,422

\- RMSE: $130,295

\- R²: 0.8812



\### KNN Comparable Sales



A K-Nearest Neighbors pipeline identifies historically similar properties using standardized property characteristics and ZIP-level candidate filtering.



\### K-Means Market Segmentation



ZIP-code housing markets are segmented using K-Means clustering.



Final ZIP-level configuration:



\- Clusters: 2

\- Silhouette Score: 0.3591



\### SHAP Explainability



SHAP TreeExplainer decomposes individual XGBoost predictions into feature-level contributions, allowing users to inspect the factors influencing each valuation.



\## Tech Stack



\### Machine Learning



\- Python

\- pandas

\- NumPy

\- scikit-learn

\- XGBoost

\- SHAP

\- joblib



\### Backend



\- FastAPI

\- Pydantic

\- Uvicorn



\### Frontend



\- Next.js

\- React

\- TypeScript

\- Tailwind CSS

\- Recharts



\### Testing



\- pytest

\- FastAPI TestClient



\## Project Structure



```text

EstateIQ/

├── backend/

│   ├── api/

│   ├── schemas/

│   ├── services/

│   └── main.py

│

├── frontend/

│   ├── app/

│   ├── lib/

│   └── public/

│

├── ml/

│   ├── artifacts/

│   ├── clustering/

│   ├── comparables/

│   ├── data/

│   ├── preprocessing/

│   └── valuation/

│

├── tests/

├── requirements.txt

└── README.md

