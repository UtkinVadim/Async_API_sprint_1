from typing import List
from http import HTTPStatus

from pydantic import BaseModel
from fastapi import Depends, HTTPException, APIRouter

from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: str
    full_name: str
    role: str
    film_ids: List[str]


@router.get("/{person_id}/", response_model=Person)
async def genre_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Person(
        uuid=person.id,
        full_name=person.fullname,
        role=person.role,
        film_ids=person.film_ids,
    )


"""
@router.get("/search/", response_model=List[Person])
async def person_search(
        query: str,
        page_number: int = Query(None, alias="page[number]"),
        page_size: int = Query(None, alias="page[size]"),
        genre_service: PersonService = Depends(get_person_service())
) -> Person:
    genre = await genre_service.get_by_id("asd")
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Person(uuid=genre.id, name=genre.name)


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


@router.get("/{person_id}/film/", response_model=List[Film])
async def genres_list(
        person_id: str,
        genre_service: PersonService = Depends(get_person_service())
) -> List[Film]:
    genres: list = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return []
"""
