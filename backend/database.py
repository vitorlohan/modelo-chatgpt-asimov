import os
from collections.abc import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()


def obrigatoria(nome: str) -> str:
    """Lê uma variável de ambiente obrigatória (do backend/.env)."""
    valor = os.getenv(nome)
    if not valor:
        raise RuntimeError(f"Variável {nome} não definida. Configure-a no backend/.env (veja o .env.example).")
    return valor


engine = create_engine(obrigatoria("DATABASE_URL"), pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db
