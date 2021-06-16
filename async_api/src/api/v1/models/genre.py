from pydantic import BaseModel


class GenreShort(BaseModel):
    """Used in:
    - Genres list
    - Details about specific genre
    """
    uuid: str
    name: str
