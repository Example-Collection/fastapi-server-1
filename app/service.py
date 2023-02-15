import requests
import time
from app.item import Item
from app.otel import tracer
import logging
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def call_server_2(item: Item):
    with tracer.start_as_current_span("server-1-call-server-2"):
        carrier = {}
        TraceContextTextMapPropagator().inject(carrier)
        header = {"traceparent": carrier["traceparent"]}
        logging.warning(f"[SERVER-1] Calling server 2 with item: {item}")
        response = requests.get(
            f"http://fastapi-server-2-svc.sangwoo-otel-poc.svc.cluster.local:8000/items-name-check?name={item.name}&price={item.price}",
            headers=header)
        # Pretend it is taking time to process, sleep for 2 seconds.
        time.sleep(2)
        logging.warning(f"[SERVER-1] Received response from server 2: {response}")
        return response
