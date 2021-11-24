from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from models.genre_response import GenreResponse
from services.genre import GenreService, get_genre_service
from strings.exceptions import GENRE_NOT_FOUND

router = APIRouter()


@router.get("/", response_model=List[GenreResponse])
async def genres_list(genre_service: GenreService = Depends(get_genre_service)) -> List[GenreResponse]:
    genres: list = await genre_service.search(body={})
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)
    return [GenreResponse(uuid=genre.id, name=genre.name) for genre in genres]


@router.get("/{genre_id}", response_model=GenreResponse)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> GenreResponse:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=GENRE_NOT_FOUND)

    return GenreResponse(uuid=genre.id, name=genre.name)
