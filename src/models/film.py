from typing import List, Optional

from pydantic import BaseModel

from models.base_data_model import BaseDataModel


class FilmPerson(BaseModel):
    id: str
    name: str


class Film(BaseDataModel):
    id: str
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[List]
    director: Optional[str]
    actors: Optional[List[FilmPerson]]
    writers: Optional[List[FilmPerson]]
