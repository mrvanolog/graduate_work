from typing import List

from pydantic import BaseModel


class Person(BaseModel):
    """Used in:
    - Search by person
    - Details about person
    """
    uuid: str
    full_name: str
    actor: List[str]
    writer: List[str]
    director: List[str]
