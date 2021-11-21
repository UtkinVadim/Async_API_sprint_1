import orjson

from typing import Optional, List

from pydantic import BaseModel

from models.utils import orjson_dumps


class Film(BaseModel):
    uuid: str
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional["List[Genre]"]
    actors: Optional["List[Person]"]
    writers: Optional["List[Person]"]
    directors: Optional["List[Person]"]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


from models.person import Person  # noqa: E402
from models.genre import Genre  # noqa: E402

Film.update_forward_refs()
