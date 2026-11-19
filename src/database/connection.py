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
    """Create a PostgreSQL connection URL from env vars, st.secrets, or DATABASE_URL."""
    secrets_diag = None
    # 1. Check Streamlit Cloud secrets
    try:
        import streamlit as st
        # In Streamlit, st.secrets is a mapping
        if hasattr(st, "secrets"):
            if "DATABASE_URL" in st.secrets:
                raw_url = str(st.secrets["DATABASE_URL"]).strip()
                if raw_url.startswith("postgres://"):
                    return raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
                elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+psycopg2://"):
                    return raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
                return raw_url
            if "POSTGRES_HOST" in st.secrets:
                user = str(st.secrets["POSTGRES_USER"]).strip()
                pwd = str(st.secrets["POSTGRES_PASSWORD"]).strip()
                host = str(st.secrets["POSTGRES_HOST"]).strip()
                port = str(st.secrets.get("POSTGRES_PORT", "5432")).strip()
                db = str(st.secrets["POSTGRES_DB"]).strip()
                return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}?sslmode=require"
            secrets_diag = f"Secrets found but DATABASE_URL key is missing. Keys present: {list(st.secrets.keys())}"
    except Exception as exc:
        secrets_diag = f"Error reading st.secrets ({exc})"

    # 2. Check environment variable DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        db_url = db_url.strip()
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+psycopg2://"):
            return db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return db_url

    # 3. Check individual env variables
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    if user and password and db and host:
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    # If neither secrets nor env vars provided:
    detail = f" [{secrets_diag}]" if secrets_diag else ""
    raise RuntimeError(
        f"Missing DATABASE_URL in Streamlit Cloud Secrets.{detail} "
        f"Please paste DATABASE_URL = \"...\" into Settings -> Secrets and click Save."
    )


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

