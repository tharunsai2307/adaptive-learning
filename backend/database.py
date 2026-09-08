from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings

# Handle SQLite vs PostgreSQL
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    # A relative SQLite path is resolved against the *current* working
    # directory, so anchor it to the repo root to keep the DB in one place.
    _raw = settings.DATABASE_URL
    _prefix = "sqlite:///"
    if _raw.startswith(_prefix) and not _raw[len(_prefix):].startswith(("/", ":memory:")):
        _abs = (Path(__file__).resolve().parent.parent / _raw[len(_prefix):]).resolve()
        _abs.parent.mkdir(parents=True, exist_ok=True)
        settings.DATABASE_URL = f"{_prefix}{_abs}"

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# SQLite-specific: enable WAL mode for better concurrency
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate() -> None:
    """
    Minimal additive migrations for the bundled SQLite dev database.

    `create_all` never alters an existing table, so columns added to a model
    after the DB was first created have to be added by hand.
    """
    inspector = inspect(engine)
    if "q_table" not in inspector.get_table_names():
        return

    columns = {c["name"] for c in inspector.get_columns("q_table")}
    if "user_id" in columns:
        return

    with engine.begin() as conn:
        # The Q-table used to be shared by every student; scope it per student.
        conn.execute(
            text("ALTER TABLE q_table ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_q_table_user_id ON q_table (user_id)"))
        # Drop the pre-split global rows: they belong to no student.
        conn.execute(text("DELETE FROM q_table WHERE user_id = 0"))


def create_tables():
    """Create all tables and apply pending migrations."""
    from . import models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)
    _migrate()
