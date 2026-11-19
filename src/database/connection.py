'''Database connection utilities.

Provides a SQLAlchemy engine based on environment variables defined in ``.env``.
The module loads ``.env`` using ``python-dotenv`` and constructs a PostgreSQL
connection URL compatible with SQLAlchemy's ``postgresql+psycopg2`` driver.

Typical usage::

    from src.database.connection import get_engine, test_connection

    engine = get_engine()
    test_connection(engine)
''' 

import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Load environment variables from .env in the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.is_file():
    load_dotenv(dotenv_path=ENV_PATH)

def _build_url() -> str:
    """Create a PostgreSQL connection URL from env vars.

    Expected variables:
        POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
    ``POSTGRES_HOST`` defaults to ``localhost`` for local Docker networking.
    """
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    if not all([user, password, db]):
        raise RuntimeError("Missing required PostgreSQL environment variables.")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def get_engine() -> Engine:
    """Return a SQLAlchemy engine with a small connection pool.

    The engine is configured for a single‑process workload (the ETL runs in the
    current process). ``pool_pre_ping`` helps recover from Docker container restarts.
    """
    url = _build_url()
    engine = create_engine(url, pool_pre_ping=True, echo=False, future=True)
    return engine


def test_connection(engine: Engine) -> None:
    """Execute a lightweight ``SELECT 1`` to verify connectivity.

    Raises an exception on failure.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.commit()

