import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

HARVESTER_URL = os.getenv("HARVESTER_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[HARVESTER_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/catalogue.ttl")
def retrieve_catalogue():
    return Response(content=open("catalogue.ttl", "rb").read(), media_type="text/turtle")


@app.get("/xnat.ttl")
def retrieve_catalogue():
    return Response(content=open("xnat.ttl", "rb").read(), media_type="text/turtle")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
