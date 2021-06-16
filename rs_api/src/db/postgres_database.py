from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.postgres_user}:" \
                          f"{settings.postgres_password}@" \
                          f"{settings.postgres_host}:{settings.postgres_port}" \
                          f"/{settings.postgres_db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
