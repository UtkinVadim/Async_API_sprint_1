import orjson

from typing import List

from pydantic import BaseModel

from models.genre import Genre
from models.person import Person
from models.utils import orjson_dumps


class Film(BaseModel):
    uuid = str
    title = str
    imdb_rating = float
    description = str
    genre = List[Genre]
    actors = List[Person]
    writers = List[Person]
    directors = List[Person]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
