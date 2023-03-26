FROM python:3.11.2-slim-bullseye AS base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt update; \
    apt --yes --no-install-recommends install python3-scipy

FROM base AS python

RUN apt update; \
    apt --yes --no-install-recommends install build-essential curl
RUN curl -sSL https://install.python-poetry.org | python - --version 1.4.1

COPY . .
RUN POETRY_VIRTUALENVS_IN_PROJECT=true /root/.local/bin/poetry install --without dev

FROM base AS runtime

ENV PATH="/.venv/bin:$PATH"

COPY . .

FROM runtime AS production

COPY --from=python /.venv /.venv
CMD ["/docker-cmd.sh"]
