from fastapi import FastAPI, Request
from rq import Queue
import logging
from worker import conn
from jobs import Job
import json
from profile import Profile

app = FastAPI()
q = Queue("nuner", connection=conn)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/ingress")
async def ingress(profile: Profile):
    q.enqueue(Job(profile.dict()).do)
    return {"message": "OK"}
