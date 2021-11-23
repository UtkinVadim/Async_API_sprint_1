import orjson

from typing import List, Optional
from pydantic import BaseModel

from models.utils import orjson_dumps


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    role: str


class Person(BaseModel):
    id: str
    fullname: str
    film_ids: Optional[List[Film]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
