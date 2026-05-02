from fastapi import FastAPI
from app.api.price import price_router
from app.api.token import tokens_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
app.include_router(price_router, prefix="/price")
app.include_router(tokens_router, prefix="/tokens")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/healthz")
def healthz():
    return {"Everything": "Ok"}
