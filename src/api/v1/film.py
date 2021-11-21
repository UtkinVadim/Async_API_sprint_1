from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str,
    from_: Optional[str] = Query(
        None,
        alias="page[number]",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
    ),
    size: Optional[str] = Query(None, alias="page[size]"),
    sort: Optional[str] = Query(None, regex="-?imdb_rating"),
    filter_genre_id: Optional[str] = Query(None, alias="filter[genre]"),
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Film(id=film.id, title=film.title)


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
    filter_person_id: Optional[str] = Query(None, alias="filter[person]"),
    # FIXME не используется, если успеет сделаю фильтрацию и по жанрам и по персоналиям
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
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
