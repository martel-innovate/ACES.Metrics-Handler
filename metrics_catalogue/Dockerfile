FROM python:3.9-slim

RUN pip install poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /metrics_catalogue
COPY  metrics_catalogue/pyproject.toml  metrics_catalogue/poetry.lock ./
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY storage/graph_base ./graph_base
COPY storage/timescaledb ./timescaledb
COPY storage/object ./object
COPY metrics_catalogue/src .

RUN poetry install
ENTRYPOINT ["poetry", "run", "uvicorn", "api:app", "--port", "8002", "--reload", "--host", "0.0.0.0"]