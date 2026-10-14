from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite database file
DATABASE_URL = "sqlite:///./sih26043.db"

# SQLite needs this for FastAPI's request/background-task usage
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session
    and always closes it afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()