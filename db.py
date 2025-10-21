from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import sqlalchemy as sa
import uuid
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    DATABASE_URL: str 
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent / ".env",  # Adjusted to same directory
        env_file_encoding="utf-8",
    )

config = Config()



Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = sa.Column(sa.UUID, primary_key=True, default=uuid.uuid4, unique=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now())
    deleted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

class Strings(BaseModel):
    __tablename__ = "strings"
    value = sa.Column(sa.String, nullable=False)
    length = sa.Column(sa.Integer, nullable=False)
    is_palindrome = sa.Column(sa.Boolean, nullable=False)
    unique_characters = sa.Column(sa.Integer, nullable=False)
    word_count = sa.Column(sa.Integer, nullable=False)
    sha256_hash = sa.Column(sa.String, nullable=False)
    character_frequency_map = sa.Column(sa.JSON, nullable=False)
    
engine = create_async_engine(url= config.DATABASE_URL)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates and yields an asynchronous database session.

    This function is an asynchronous generator that creates a new database session
    using the async_session factory and yields it. The session is automatically
    closed when the generator is exhausted or the context is exited.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session object.

    Usage:
        async for session in get_session():
            # Use the session for database operations
            ...
    """
    async with async_session() as session:
        yield session


async def init_db():
    """
    Initialize the database by creating all tables defined in the Base metadata.

    This asynchronous function uses the SQLAlchemy engine to create all tables
    that are defined in the Base metadata. It's typically used when setting up
    the database for the first time or after a complete reset.

    The function uses a connection from the engine and runs the create_all
    method synchronously within the asynchronous context.
    """
    async with engine.begin() as conn:
        # Use run_sync to call the synchronous create_all method in an async context
        await conn.run_sync(Base.metadata.create_all)
        print(Base.metadata.tables.keys())

async def drop_db():
    """
    Drop all tables in the database.

    This asynchronous function uses the SQLAlchemy engine to drop all tables
    that are defined in the Base metadata. It's typically used when you want
    to completely reset the database structure.

    Caution: This operation will delete all data in the tables. Use with care.
    """
    async with engine.begin() as conn:
        # Use run_sync to call the synchronous drop_all method in an async context
        await conn.run_sync(Base.metadata.drop_all)
