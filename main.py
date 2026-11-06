import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

MODELO = "openai/gpt-4o-mini"

app = FastAPI()


class Entrada(BaseModel):
    mensagem: str


@app.post("/send_message")
def send_message(entrada: Entrada):
    resposta = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={"model": MODELO, "messages": [{"role": "user", "content": entrada.mensagem}]},
        timeout=60,
    )
    if not resposta.ok:
        raise HTTPException(status_code=resposta.status_code, detail=resposta.json())
    return {"resposta": resposta.json()["choices"][0]["message"]["content"]}
