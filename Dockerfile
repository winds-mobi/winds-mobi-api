FROM python:3.11.9-slim-bookworm AS base

RUN apt update; \
    apt --yes --no-install-recommends install python3-scipy

FROM base AS python

RUN apt update; \
    apt --yes --no-install-recommends install build-essential curl
RUN curl -sSL https://install.python-poetry.org | python - --version 1.8.3

COPY . .
RUN POETRY_VIRTUALENVS_IN_PROJECT=true /root/.local/bin/poetry install --without dev

FROM base AS runtime

ENV PATH="/.venv/bin:$PATH"

COPY . .

FROM runtime AS production

COPY --from=python /.venv /.venv
CMD ["/docker-cmd.sh"]
