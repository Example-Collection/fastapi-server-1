from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.item import Item
from app.service import call_server_2
from app.otel import tracer
import logging

app = FastAPI()


@app.post("/items", status_code=201)
async def server_1_handler(item: Item):
    with tracer.start_as_current_span("server-1-handler"):
        logging.warning(f"[SERVER-1] Received item: {item}")
        result = call_server_2(item)
        if result.status_code != 200:
            logging.warning(f"[SERVER-1] Server 2 returned non-200 status code. (status_code: {result.status_code})")
            raise HTTPException(status_code=result.status_code, detail=result.json())
        return JSONResponse(content=jsonable_encoder(result.json()), status_code=201)
