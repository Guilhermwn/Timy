import ast
import os
from base64 import b64decode
from typing import List, Optional

import firebase_admin
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore
from pydantic import BaseModel

load_dotenv()

json = ast.literal_eval(b64decode(os.getenv("FIREBASE_CREDENTIAL_JSON")).decode())

# Initialize Firebase Admin SDK
cred = credentials.Certificate(json)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Create FastAPI instance
app = FastAPI()


class Timy(BaseModel):
    data: str
    saida_casa: Optional[str] = None
    chegada_DIA1: Optional[str] = None
    saida_DIA1: Optional[str] = None
    chegada_ufs: Optional[str] = None
    saida_ufs: Optional[str] = None
    chegada_DIA2: Optional[str] = None
    saida_DIA2: Optional[str] = None
    chegada_casa: Optional[str] = None


@app.get("/")
def home():
    return {
        "Project": "Timy",
        "Author": {"Name": "Guilhermwn", "Email": "guilhermwn.franco@gmail.com"},
    }


@app.get("/ping")
def ping_pong():
    return "pong"


@app.post("/add", response_model=Timy)
def add_info(entry: Timy):
    new_entry = {k: v for k, v in entry.model_dump().items() if v}
    doc_ref = db.collection("timy").add(new_entry)
    return new_entry


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
