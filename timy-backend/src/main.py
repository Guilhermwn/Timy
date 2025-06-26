import os
import tempfile
from base64 import b64decode
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import fireo
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fireo.fields import TextField
from fireo.models import Model
from pydantic import BaseModel

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting connection")
    cred_b64 = os.getenv("FIREBASE_CREDENTIAL_JSON")
    if not cred_b64:
        raise RuntimeError("Variável FIREBASE_CREDENTIAL_JSON não definida")

    cred_json = b64decode(cred_b64).decode("utf-8")
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        tmp.write(cred_json)
        tmp.flush()
        file_path = Path(tmp.name)

    fireo.connection(from_file=file_path)
    yield
    print("Closing connection")
    os.unlink(file_path)


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EntrySchema(Model):
    data = TextField()
    saida_casa = TextField()
    chegada_DIA1 = TextField()
    saida_DIA1 = TextField()
    chegada_ufs = TextField()
    saida_ufs = TextField()
    chegada_DIA2 = TextField()
    saida_DIA2 = TextField()
    chegada_casa = TextField()

    class Meta:
        collection_name = "Timy"


class EntryModel(BaseModel):
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
    return {"Hello": "World"}


@app.get("/ping")
def ping_pong():
    return "pong"


@app.post("/add")
def add_info(info: EntryModel):
    present = EntrySchema.collection.filter("data", "==", info.data).get()
    e = EntrySchema.from_dict(
        {k: v for k, v in info.model_dump().items() if v is not None}
    )

    if present:
        e.update(present.key)
        return {"key": present.key, "activity": "Atualizado"}
    else:
        e.save()
        return {"key": e.key, "activity": "Adicionado"}

@app.get("/list")
def list():
    list = EntrySchema.collection.fetch()
    return [{"data":item.data} for item in list]
        
        


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
