from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import router

app = FastAPI(title="AI Financial Report Generator")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router)