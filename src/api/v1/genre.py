from typing import List
from http import HTTPStatus

from pydantic import BaseModel
from fastapi import Depends, HTTPException, APIRouter

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


@router.get("/", response_model=List[Genre])
async def genres_list(
    genre_service: GenreService = Depends(get_genre_service),
) -> List[Genre]:
    genres: list = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return [Genre(uuid=genre.id, name=genre.name) for genre in genres]


@router.get("/{genre_id}/", response_model=Genre)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(uuid=genre.id, name=genre.name)
