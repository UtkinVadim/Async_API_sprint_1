import orjson

from typing import Optional, List

from pydantic import BaseModel

from models.utils import orjson_dumps


class FilmPerson(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[List]
    director: Optional[str]
    actors: Optional[List[FilmPerson]]
    writers: Optional[List[FilmPerson]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
