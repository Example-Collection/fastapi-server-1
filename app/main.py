from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.item import Item
from app.service import call_server_2
from app.otel import tracer
from opentelemetry.instrumentation.logging import LoggingInstrumentor

import logging

app = FastAPI()

LoggingInstrumentor().instrument(set_logging_format=True,
                                 logging_format=' trace_id=%(otelTraceID)s span_id=%(otelSpanID)s - %(message)s')


@app.post("/items", status_code=201)
async def server_1_handler(item: Item, request: Request):
    with tracer.start_as_current_span("server-1-handler") as span:
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
