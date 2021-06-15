from sqlalchemy import Column, String, ARRAY

from postgres_database import Base


class UserPrediction(Base):
    __tablename__ = "users"

    user_id = Column(String)
    rec_movie_id = Column(String)


class MoviePrediction(Base):
    __tablename__ = "movies"

    movie_id = Column(String)
    rec_movie_id = Column(ARRAY(String()))
