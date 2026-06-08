FROM python:3.11.15-slim-bookworm AS base

RUN apt update; \
    apt --yes --no-install-recommends install python3-scipy

FROM base AS python

RUN apt update; \
    apt --yes --no-install-recommends install build-essential curl
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

COPY . .
RUN uv sync --no-dev --locked

FROM base AS runtime

ENV PATH="/.venv/bin:$PATH"

COPY . .

FROM runtime AS production

COPY --from=python /.venv /.venv
CMD ["/docker-cmd.sh"]
