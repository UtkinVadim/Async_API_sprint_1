import orjson

from typing import List
from pydantic import BaseModel

from models.film import Film
from models.utils import orjson_dumps


class Person(BaseModel):
    uuid: str
    full_name: str
    role: str
    film_ids: List[Film]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
