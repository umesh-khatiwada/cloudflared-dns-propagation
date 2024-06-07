import logging
import os
from fastapi import Depends, FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from routes.domain import router as domain_route


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# routes

@app.on_event("startup")
def startup_db_client():
    logging.basicConfig(level=logging.INFO)

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(domain_route, tags=["domain"],prefix="/v1/domain")

