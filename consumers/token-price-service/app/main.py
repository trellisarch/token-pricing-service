from os import getenv
from fastapi import FastAPI
from app.api.price import price_router
from app.api.test import test_router
from app.api.token import tokens_router

app = FastAPI()
app.include_router(price_router, prefix="/price")
app.include_router(tokens_router, prefix="/tokens")
if getenv("ENVIRONMENT", "prod") != "dev":
    app.include_router(test_router, prefix="/test")


@app.get("/healthz")
def healthz():
    return {"Everything": "Ok"}
