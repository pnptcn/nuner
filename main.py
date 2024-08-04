import logging
from profile import Profile

from extract_job import Job
from fastapi import FastAPI
from rq import Queue
from worker import conn

app = FastAPI()
q = Queue("nuner", connection=conn)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/ingress")
async def ingress(profile: Profile):
    q.enqueue(Job(profile.dict()).do)
    return {"message": "OK"}
