async def generate_body(query, from_, size) -> dict:
    """
    Создаёт тело запроса к эластику.
    Если query не задан - возвращает все документы.

    :param query:
    :param from_: номер выводимой страницы
    :param size: кол-во данных (документов) на странице
    :return:
    """

    if not query:
        match = {"match_all": {}}
    else:
        match = {"multi_match": {"query": query}}

    body = {"query": {"bool": {"must": [match]}}}

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
    Добавляет в тело запроса условие фильтрации по жанру.
    Если делать поиск и по жанрам и по актёрам, вместо must нужно поставить should.

    :param body:
    :param filter_genre:
    :return:
    """
    filter_dict = {"bool": {"filter": {"bool": {"must": {"term": {"genre": filter_genre.name}}}}}}

    body["query"]["bool"]["must"].append(filter_dict)
    return body
