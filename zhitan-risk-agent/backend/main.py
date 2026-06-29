from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.pipeline import run_pipeline
from data.sample_companies import COMPANY_SHORTCUTS
from schemas.risk import CompanyShortcut, QueryRequest, RiskReport

app = FastAPI(title="职探 Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "zhitan-risk-agent"}


@app.get("/api/companies", response_model=dict[str, list[CompanyShortcut]])
def list_companies():
    return {"companies": COMPANY_SHORTCUTS}


@app.post("/api/query", response_model=RiskReport)
def query_company(request: QueryRequest):
    return run_pipeline(request)
