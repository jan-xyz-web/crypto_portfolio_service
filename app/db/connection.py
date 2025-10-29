from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection

_engine: Engine | None = None


def get_engine(db_path: str) -> Engine:
    """Create SQLAlchemy engine with SQLite pragmas."""
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return _engine


def get_connection() -> Connection:
    """Get connection from engine. Use for transactions."""
    from app.config import settings
    engine = get_engine(settings.db_path)
    return engine.connect()
