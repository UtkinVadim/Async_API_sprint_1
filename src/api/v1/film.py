from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import Film
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class ShortFilm(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]


class FilmDetailed(Film):
    """
    Класс модели с полной информацией о фильме
    """


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=FilmDetailed)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    """
    Отдаёт полную информацию по фильму
    GET /api/v1/film/<uuid:UUID>/

    :param film_id:
    :param film_service:
    :return:
    """

    film = await film_service.get_by_id(id_=film_id, index="movies")
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return FilmDetailed(**film.dict())


# GET /api/v1/film?filter[genre]=<uuid:UUID>&sort=-imdb_rating&page[size]=50&page[number]=1
# GET /api/v1/film?sort=-imdb_rating&page[size]=50&page[number]=1
# Полная информация по фильму.
# /api/v1/film/<uuid:UUID>/
@router.get("/search/")
async def film_search(
    query: Optional[str] = Query("", alias="query"),
    from_: Optional[str] = Query(
        None,
        alias="page[number]",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
    ),
    size: Optional[str] = Query(None, alias="page[size]"),
    sort: Optional[str] = Query(None, regex="-?imdb_rating"),
    filter_genre_id: Optional[str] = Query(None, alias="filter[genre]"),
    # FIXME не используется, если успеет сделаю фильтрацию и по жанрам и по персоналиям
    filter_person_id: Optional[str] = Query(None, alias="filter[person]"),
    film_service: FilmService = Depends(get_film_service),
) -> list[ShortFilm]:
    """
    Поиск по фильмам с пагинацией, фильтрацией по жанрам и сортировкой

    :param query:
    :param from_:
    :param size:
    :param sort:
    :param filter_genre_id:
    :param filter_person_id:
    :param film_service:
    :return:
    """
    body = await generate_body(query, from_, size)

    if sort:
        body = await add_sort_to_body(body, sort)

    if filter_genre_id:
        # FIXME обработать ситуацию если жанр не будет найден
        filter_genre = await film_service.get_by_id(filter_genre_id, index="genre")
        body = await add_filter_to_body(body, filter_genre)

    result = await film_service.search(index="movies", body=body)

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return result


async def generate_body(query, from_, size) -> dict:
    """
    Создаёт тело запроса к эластику

    :param query:
    :param from_: номер выводимой страницы
    :param size: кол-во данных (документов) на странице
    :return:
    """
    if not query:
        query = ""

    body = {"query": {"bool": {"must": [{"multi_match": {"query": query}}]}}}

    if from_:
        body["from"] = from_
    if size:
        body["size"] = size

    return body


async def add_sort_to_body(body, sort) -> dict:
    """
    Добавляет в тело зарпоса сортировку

    :param body:
    :param sort:
    :return:
    """
    if "-" in sort:
        sort = [{"imdb_rating": "desc"}]
    else:
        sort = [{"imdb_rating": "asc"}]
    body["sort"] = sort
    return body


async def add_filter_to_body(body, filter_genre) -> dict:
    """
    Добавляет в тело запроса условие фильтрации по жанру

    :param body:
    :param filter_genre:
    :return:
    """
    filter_dict = {
        "bool": {
            "filter": {
                "bool": {
                    "must": {  # если делать поиск и по жанрам и по актёрам сюда нужно поставить should
                        "term": {"genre": filter_genre.name}
                    }
                }
            }
        }
    }

    body["query"]["bool"]["must"].append(filter_dict)
    return body
