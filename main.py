import logging
import os
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from controller.audio_controller import html_form_router
# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
from controller.native_form_controller import native_form_router

import hashlib

project_id = "hack-finnovate"
cred = credentials.ApplicationDefault()

DATABASE = "stof"
USERS = "users"

app = FastAPI()

app.include_router(html_form_router)
app.include_router(native_form_router)

origins = [
    "http://169.254.8.129",
    "http://169.254.*",
    "http://127.0.0.*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

db = firestore.client()


@app.middleware("http")
async def logger(request: Request, call_next):
    logging.info(f"Request from {request.client}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response


@app.middleware("http")
async def authentication(request: Request, call_next):
    logging.info(f"Request for authentication")
    auth_token = request.headers['Authorization']
    auth_doc = db.collection(USERS).document(u'tldyeTF6VlnAuKWQ7O8U').get().to_dict()
    up_sha = hashlib.sha256(f'{auth_doc["username"]}{auth_doc["password"]}'.encode()).hexdigest()
    if auth_token == up_sha:
        response = await call_next(request)
    else:
        response = {
            "status": "Unauthorized"
        }
    return response


@app.get("/")
async def root():
    return {
        "hello": "world"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.environ.get("PORT", 8080))
