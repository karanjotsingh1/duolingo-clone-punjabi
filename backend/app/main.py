"""FastAPI entry point:  uvicorn app.main:app --reload"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .seed import seed


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed()          # create tables + sample data on first start
    yield


app = FastAPI(title="Duolingo Clone API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
