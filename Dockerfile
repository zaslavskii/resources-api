FROM python:3.7-alpine3.9

ENV PYTHONUNBUFFERED 1
ENV PATH="/venv/bin:${PATH}"
ENV POETRY_VERSION=0.12.16

WORKDIR /app

RUN apk update && \
    apk add --no-cache curl build-base postgresql-dev gcc

COPY poetry.lock pyproject.toml /app/

RUN set -o pipefail \
   && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/${POETRY_VERSION}/get-poetry.py > get-poetry.py \
   && python get-poetry.py --version ${POETRY_VERSION} -y \
   && . ${HOME}/.poetry/env \
   && python -m venv /venv \
   && . /venv/bin/activate \
   && poetry install --no-dev

COPY src /app/src

COPY start.sh /usr/bin
RUN chmod 700 /usr/bin/start.sh


CMD ["start.sh"]

EXPOSE 8000
