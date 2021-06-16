from dataclasses import dataclass
from datetime import datetime


@dataclass
class FilmRow():
    fw_id: str
    title: str
    description: str
    rating: float
    type: str
    created: datetime
    modified: datetime
    role: str
    p_id: str
    full_name: str
    g_id: str
    name: str


@dataclass
class GenreRow():
    g_id: str
    name: str


@dataclass
class PersonRow():
    p_id: str
    full_name: str
    role: str
    f_id: str
