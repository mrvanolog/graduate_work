from sqlalchemy import Column, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID

import uuid

from db.postgres_database import Base


class UserPrediction(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'rs-predictions'}

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rec_movie_id = Column(String)


class MoviePrediction(Base):
    __tablename__ = "movies"
    __table_args__ = {'schema': 'rs-predictions'}

    movie_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rec_movie_id = Column(ARRAY(String()))
