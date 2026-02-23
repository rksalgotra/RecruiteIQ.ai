import uuid
import time
import logging
from typing import Callable, List

from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.embedding_service import generate_embedding
from core.database import get_db
from core.models_db import Resume, CandidateScore

# ==============================
# Prometheus
# ==============================
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# ==============================
# Rate Limiting
# ==============================
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# ==============================
# OpenTelemetry
# ==============================
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# ============================================================
# App Initialization
# ============================================================

app = FastAPI(
    title="TalentAIQ - Enterprise Edition",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Logging
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("talentaiq")

# ============================================================
# Correlation Middleware
# ============================================================

@app.middleware("http")
async def correlation_middleware(request: Request, call_next: Callable):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    start_time = time.time()
    response: Response = await call_next(request)
    duration = round(time.time() - start_time, 4)

    response.headers["X-Correlation-ID"] = correlation_id

    logger.info(
        {
            "event": "request_completed",
            "correlation_id": correlation_id,
            "path": request.url.path,
            "duration_sec": duration,
            "status_code": response.status_code,
        }
    )

    return response


# ============================================================
# Rate Limiting
# ============================================================

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "RATE_LIMIT_EXCEEDED",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


# ============================================================
# Telemetry
# ============================================================

resource = Resource(attributes={"service.name": "talentaiq-api"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)


# ============================================================
# Metrics
# ============================================================

REQUEST_COUNT = Counter("talentaiq_requests_total", "Total requests", ["endpoint"])
REQUEST_LATENCY = Histogram("talentaiq_request_latency_seconds", "Latency", ["endpoint"])
ERROR_COUNT = Counter("talentaiq_errors_total", "Total errors", ["error_type"])


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ============================================================
# API Models
# ============================================================

class MatchRequest(BaseModel):
    candidate_name: str
    skills: List[str]
    experience_years: int


class MatchResponse(BaseModel):
    candidate_name: str
    score: float
    category: str
    explanation: str


# ============================================================
# Scoring Engine
# ============================================================

class ScoringEngine:

    @staticmethod
    def calculate_score(payload: MatchRequest) -> MatchResponse:

        normalized_skills = [s.lower() for s in payload.skills]
        score = 0.5
        skill_hits = []

        if "aws" in normalized_skills:
            score += 0.2
            skill_hits.append("AWS")

        if "python" in normalized_skills:
            score += 0.15
            skill_hits.append("Python")

        if "docker" in normalized_skills:
            score += 0.1
            skill_hits.append("Docker")

        if payload.experience_years >= 5:
            score += 0.05

        score = round(min(score, 1.0), 2)

        if score >= 0.85:
            category = "Strong Match"
        elif score >= 0.65:
            category = "Moderate Match"
        else:
            category = "Weak Match"

        explanation = (
            f"Matched skills: {', '.join(skill_hits) if skill_hits else 'None'}. "
            f"Experience: {payload.experience_years} years."
        )

        return MatchResponse(
            candidate_name=payload.candidate_name,
            score=score,
            category=category,
            explanation=explanation,
        )


# ============================================================
# Match Endpoint
# ============================================================

@app.post("/api/v1/match", response_model=MatchResponse)
@limiter.limit("20/minute")
async def match_candidate(
    request: Request,
    payload: MatchRequest,
    db: Session = Depends(get_db),
):

    endpoint_label = "match_v1"

    with tracer.start_as_current_span("candidate_match_operation"):
        REQUEST_COUNT.labels(endpoint=endpoint_label).inc()
        start_time = time.time()

        try:
            # Step 1: Rule-based scoring
            response = ScoringEngine.calculate_score(payload)

            # Step 2: Generate real embedding
            resume_text = (
                f"{payload.candidate_name}. "
                f"Skills: {', '.join(payload.skills)}. "
                f"Experience: {payload.experience_years} years."
            )

            resume_embedding = generate_embedding(resume_text)

            # Debug (safe to remove later)
            print("DEBUG EMBEDDING FROM API:", resume_embedding[:5])

            # Step 3: Persist Resume
            resume_obj = Resume(
                candidate_name=payload.candidate_name,
                raw_text=resume_text,
                embedding=resume_embedding,
            )

            db.add(resume_obj)
            db.flush()

            # Step 4: Persist Score
            score_obj = CandidateScore(
                job_id=None,
                resume_id=resume_obj.id,
                skill_score=response.score,
                embedding_score=0.0,
                experience_score=float(payload.experience_years),
                final_score=response.score,
                category=response.category
            )

            db.add(score_obj)
            db.commit()

            return response

        except Exception as e:
            db.rollback()
            raise e

        finally:
            REQUEST_LATENCY.labels(endpoint=endpoint_label).observe(
                time.time() - start_time
            )