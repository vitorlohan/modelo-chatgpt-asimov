import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db, obrigatoria
from models import Usuario

JWT_SECRET = obrigatoria("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

password_hash = PasswordHash.recommended()  # Argon2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Hash usado quando o usuário não existe, para o login levar o mesmo tempo
# nos dois casos e não revelar quais nomes de usuário estão cadastrados.
_HASH_FALSO = password_hash.hash("senha-inexistente")


def hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def autenticar(db: Session, usuario: str, senha: str) -> Usuario | None:
    encontrado = db.scalar(select(Usuario).where(Usuario.usuario == usuario.lower()))
    if encontrado is None:
        password_hash.verify(senha, _HASH_FALSO)
        return None
    return encontrado if password_hash.verify(senha, encontrado.senha_hash) else None


def criar_token(usuario: Usuario) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(usuario.id), "exp": expira}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def usuario_atual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    """Dependência que exige um JWT válido e devolve o usuário dono dele."""
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise erro
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise erro
    return usuario
