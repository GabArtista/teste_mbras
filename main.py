"""FastAPI application exposing the MBRAS analyzer endpoint."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import analyzer
from app.analyzer import AnalysisError
from app.schemas import AnalyzeFeedRequest

app = FastAPI(
    title="MBRAS — Backend Challenge API",
    version="1.0.0",
    description="Sistema de análise de sentimentos e engajamento em tempo real.",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors into 400 responses."""
    details = exc.errors()
    for error in details:
        ctx = error.get("ctx")
        if ctx and "error" in ctx:
            ctx["error"] = str(ctx["error"])
    return JSONResponse(
        status_code=400,
        content={
            "error": "Payload inválido. Verifique os campos enviados.",
            "code": "INVALID_PAYLOAD",
            "details": details,
        },
    )


@app.post("/analyze-feed")
async def analyze_feed_endpoint(request_body: AnalyzeFeedRequest):
    """Analyze a feed of messages and compute metrics."""
    start_time = time.perf_counter()
    try:
        analysis = analyzer.analyze_feed(request_body, request_time=datetime.now(timezone.utc))
    except AnalysisError as err:
        if str(err) == "UNSUPPORTED_TIME_WINDOW":
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Valor de janela temporal não suportado na versão atual",
                    "code": "UNSUPPORTED_TIME_WINDOW",
                },
            )
        raise

    processing_time_ms = int((time.perf_counter() - start_time) * 1000)
    analysis["processing_time_ms"] = processing_time_ms

    return {"analysis": analysis}
