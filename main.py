import logging
from fastapi import FastAPI
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

@app.on_event("startup")
def startup_event():
    logging.basicConfig(level=logging.INFO)
    # Initialize MongoDB client if needed
    # app.mongodb_client = MongoClient(os.getenv("MONGODB_URI"))

@app.on_event("shutdown")
def shutdown_event():
    # Close MongoDB client if needed
    # app.mongodb_client.close()
    pass

app.include_router(domain_route, tags=["domain"], prefix="/v1/domain")
