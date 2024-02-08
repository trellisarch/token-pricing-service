import sys

from fastapi import FastAPI
from app.api.price import price_router
from app.api.token import tokens_router

app = FastAPI()
app.include_router(price_router, prefix="/price")
app.include_router(tokens_router, prefix="/tokens")


@app.get("/healthz")
def healthz():
    return {"Everything": "Ok"}
