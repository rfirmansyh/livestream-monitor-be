from typing import TypeVar
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from config import base_config

T = TypeVar("T", bound=SQLModel)

async_engine = create_async_engine(
  base_config.DATABASE_URL,
  echo=True,
  future=True
)

async_session = sessionmaker(
  bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def get_session() -> AsyncSession:
  async with async_session() as session:
    yield session
async def get_session_raw() -> AsyncSession:
  return async_session()