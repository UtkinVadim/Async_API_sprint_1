from typing import Optional

from pydantic import BaseModel

from models.base_orjson_model import BaseOrjsonModel


class ShortFilmResponse(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: Optional[float]


class FilmPersonResponse(BaseModel):
    id: str
    name: str


class FilmDetailResponse(BaseOrjsonModel):
    """
    Модель респонса с полной информацией о фильме
    """

    id: str
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[list]
    director: Optional[str]
    actors: Optional[list[FilmPersonResponse]]
    writers: Optional[list[FilmPersonResponse]]
