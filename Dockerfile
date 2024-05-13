FROM python:3.12

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --upgrade pip \
  && pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

COPY . .

COPY ./.env /app/.env
COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod -R +x ./entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]
