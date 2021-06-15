import orjson
from pydantic import BaseModel


class Genre(BaseModel):
    uuid: str
    name: str

    class Config:
        # replacing standard json process by a faster one
        json_loads = orjson.loads
        json_dumps = orjson.dumps
