import orjson

from typing import List, Optional
from pydantic import BaseModel

from models.utils import orjson_dumps


class FilmId(BaseModel):
    id: str


class Person(BaseModel):
    id: str
    fullname: str
    role: str
    film_ids: Optional[List[FilmId]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
