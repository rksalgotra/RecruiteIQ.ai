import uuid
import time
import logging
from typing import Callable, List

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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
    title="RecruitIQ - Enterprise Edition",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Logging Setup
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recruitiq")

# ============================================================
# Correlation ID Middleware
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
            "method": request.method,
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
            "message": "Too many requests",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )

# ============================================================
# OpenTelemetry
# ============================================================

resource = Resource(attributes={"service.name": "recruitiq-api"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)

# ============================================================
# Prometheus Metrics
# ============================================================

REQUEST_COUNT = Counter(
    "recruitiq_requests_total",
    "Total number of requests",
    ["endpoint"]
)

REQUEST_LATENCY = Histogram(
    "recruitiq_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

ERROR_COUNT = Counter(
    "recruitiq_errors_total",
    "Total number of errors",
    ["error_type"]
)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ============================================================
# Structured Errors
# ============================================================

class RecruitIQError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


@app.exception_handler(RecruitIQError)
async def recruitiq_exception_handler(request: Request, exc: RecruitIQError):
    ERROR_COUNT.labels(error_type=exc.code).inc()
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "message": exc.message,
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    ERROR_COUNT.labels(error_type="INTERNAL_ERROR").inc()
    logger.exception(str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "Unexpected system failure",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )

# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============================================================
# API v1 Models
# ============================================================

class MatchRequest(BaseModel):
    candidate_name: str = Field(..., example="Rajesh Kumar")
    skills: List[str] = Field(..., example=["AWS", "Python", "Docker"])
    experience_years: int = Field(..., example=5)


class MatchResponse(BaseModel):
    candidate_name: str
    score: float
    category: str
    explanation: str

# ============================================================
# Scoring Service (Separated Cleanly)
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
# API v1 Match Endpoint
# ============================================================

@app.post("/api/v1/match", response_model=MatchResponse)
@limiter.limit("20/minute")
async def match_candidate(request: Request, payload: MatchRequest):

    endpoint_label = "match_v1"

    with tracer.start_as_current_span("candidate_match_operation"):
        REQUEST_COUNT.labels(endpoint=endpoint_label).inc()
        start_time = time.time()

        try:
            if not payload.candidate_name:
                raise RecruitIQError(
                    code="VALIDATION_ERROR",
                    message="Candidate name missing"
                )

            response = ScoringEngine.calculate_score(payload)
            return response

        finally:
            REQUEST_LATENCY.labels(endpoint=endpoint_label).observe(
                time.time() - start_time
            )