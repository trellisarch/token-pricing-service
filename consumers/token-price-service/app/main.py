from fastapi import FastAPI
from app.api.price import price_router
from app.api.token import tokens_router
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import start_http_server

app = FastAPI()
app.include_router(price_router, prefix="/price")
app.include_router(tokens_router, prefix="/tokens")

start_http_server(5990)
Instrumentator().instrument(app)


@app.get("/healthz")
def healthz():
    return {"Everything": "Ok"}
