from fastapi import FastAPI

from backend.api.routes import router

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="EstateIQ API",
    description=(
        "Machine-learning powered "
        "real-estate intelligence platform."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():

    return {
        "application": "EstateIQ",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",

        "services": {
            "api": "available",
            "valuation_model": "available",
        },
    }