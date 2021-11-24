from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.film import generate_body
from models.person_response import PersonFilmResponse, PersonResponse
from services.person import PersonService, get_person_service
from strings.exceptions import PERSON_NOT_FOUND

router = APIRouter()


@router.get("/search", response_model=List[PersonResponse])
async def person_search(
    query: str,
    page_number: int = Query(None, alias="page[number]"),
    page_size: int = Query(None, alias="page[size]"),
    service: PersonService = Depends(get_person_service),
) -> List[PersonResponse]:
    body = await generate_body(query, page_number, page_size)
    searched_persons = await service.search(body=body)
    if not searched_persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)
    return [
        PersonResponse(uuid=person.id, full_name=person.fullname, films=[{film.id: film.role} for film in person.film_ids])
        for person in searched_persons
    ]


@router.get("/{person_id}", response_model=PersonResponse)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonResponse:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)
    return PersonResponse(uuid=person.id, full_name=person.fullname, films=[{film.id: film.role} for film in person.film_ids])


@router.get("/{person_id}/film", response_model=List[PersonFilmResponse])
async def person_films(person_id: str, person_service: PersonService = Depends(get_person_service)) -> List[PersonFilmResponse]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return [PersonFilmResponse(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in person.film_ids]
