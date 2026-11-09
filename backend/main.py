import os
from contextlib import asynccontextmanager
from typing import Annotated

import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import autenticar, criar_token, hash_senha, usuario_atual
from database import Base, engine, get_db
from models import Usuario

MODELO = "openai/gpt-4o-mini"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # cria a tabela de usuários se não existir
    yield


app = FastAPI(lifespan=lifespan)

# Libera o frontend (aberto pelo navegador) a chamar a API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Entrada(BaseModel):
    mensagem: str


class Cadastro(BaseModel):
    usuario: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    senha: str = Field(min_length=8, max_length=128)


class UsuarioPublico(BaseModel):
    id: int
    usuario: str


@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UsuarioPublico)
def register(dados: Cadastro, db: Annotated[Session, Depends(get_db)]):
    usuario = Usuario(usuario=dados.usuario.lower(), senha_hash=hash_senha(dados.senha))
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Esse nome de usuário já está em uso.")
    return UsuarioPublico(id=usuario.id, usuario=usuario.usuario)


@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    usuario = autenticar(db, form.username, form.password)
    if usuario is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": criar_token(usuario), "token_type": "bearer"}


@app.get("/me", response_model=UsuarioPublico)
def me(usuario: Annotated[Usuario, Depends(usuario_atual)]):
    return UsuarioPublico(id=usuario.id, usuario=usuario.usuario)


@app.post("/send_message")
def send_message(entrada: Entrada, usuario: Annotated[Usuario, Depends(usuario_atual)]):
    resposta = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={"model": MODELO, "messages": [{"role": "user", "content": entrada.mensagem}]},
        timeout=60,
    )
    if not resposta.ok:
        raise HTTPException(status_code=resposta.status_code, detail=resposta.json())
    return {"resposta": resposta.json()["choices"][0]["message"]["content"]}


def start():
    """Atalho `uv run start`: sobe a API em http://127.0.0.1:8000."""
    import uvicorn

    uvicorn.run("main:app", reload=True, reload_dirs=[os.path.dirname(__file__)])
