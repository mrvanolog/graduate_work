from typing import List

import orjson
from pydantic import BaseModel


class Person(BaseModel):
    uuid: str
    full_name: str
    actor: List[str]
    writer: List[str]
    director: List[str]

    class Config:
        # replacing standard json process by a faster one
        json_loads = orjson.loads
        json_dumps = orjson.dumps
