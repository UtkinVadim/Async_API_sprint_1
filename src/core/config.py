import os
from logging import config as logging_config

from core.logger import LOGGING

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=False))

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Настройки сервера
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
