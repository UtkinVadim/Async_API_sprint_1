import orjson
from pydantic import BaseModel

from models.utils import orjson_dumps


class Genre(BaseModel):
    id: str
    name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
