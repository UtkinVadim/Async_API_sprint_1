from http import HTTPStatus
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from api.v1.film import generate_body
from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: str
    full_name: str
    films: List[Dict]


@router.get("/search", response_model=List[Person])
async def person_search(
    query: str,
    page_number: int = Query(None, alias="page[number]"),
    page_size: int = Query(None, alias="page[size]"),
    service: PersonService = Depends(get_person_service),
) -> List[Person]:
    body = await generate_body(query, page_number, page_size)
    searched_persons = await service.search(body=body)
    if not searched_persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return [
        Person(uuid=person.id, full_name=person.fullname, films=[{film.id: film.role} for film in person.film_ids])
        for person in searched_persons
    ]


@router.get("/{person_id}", response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return Person(uuid=person.id, full_name=person.fullname, films=[{film.id: film.role} for film in person.film_ids])


class PersonFilm(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]


@router.get("/{person_id}/film", response_model=List[PersonFilm])
async def person_films(person_id: str, person_service: PersonService = Depends(get_person_service)) -> List[PersonFilm]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return [PersonFilm(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in person.film_ids]
