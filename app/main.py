from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.item import Item
from app.service import call_server_2
from app.otel import tracer
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.logging import LoggingInstrumentor

import logging


def get_trace_parent_header(request: Request):
    return request.headers.get("traceparent")


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


LoggingInstrumentor().instrument(set_logging_format=True,
                                 logging_format=' trace_id=%(otelTraceID)s span_id=%(otelSpanID)s - %(message)s')


@app.post("/items", status_code=201)
async def server_1_handler(item: Item, request: Request):
    traceparent = get_trace_parent_header(request)
    carrier = {"traceparent": traceparent}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    with tracer.start_as_current_span("server-1-handler", context=ctx) as span:
        span.set_attribute("item_name", item.name)
        span.set_attribute("item_price", item.price)
        span.set_attribute("ip", request.client.host)
        span.set_attribute("path", request.url.path)
        logging.warning(f"[SERVER-1] Received item: {item}")
        result = call_server_2(item)
        if result.status_code != 200:
            logging.warning(f"[SERVER-1] Server 2 returned non-200 status code. (status_code: {result.status_code})")
            raise HTTPException(status_code=result.status_code, detail=result.json())
        return JSONResponse(content=jsonable_encoder(result.json()), status_code=201)
