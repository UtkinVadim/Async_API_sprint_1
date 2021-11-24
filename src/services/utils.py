async def flatten_json(obj):
    """
    "Плющит" входной объект.

    Пример работы:
    {'a': {'b': 'c'}} -> ['a', 'b', 'c']

    :param obj:
    :return:
    """
    body_list = []

    async def flatten(x):
        if isinstance(x, dict):
            for a in x:
                body_list.append(a)
                await flatten(x[a])
        elif isinstance(x, list):
            for a in x:
                await flatten(a)
        else:
            body_list.append(x)

    await flatten(obj)
    return body_list
