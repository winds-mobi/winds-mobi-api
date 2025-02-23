winds-mobi-api
==============

[![Uptime](https://img.shields.io/uptimerobot/ratio/m792621614-9a09b39a1095a00ab7aac360?label=API%202.3)](https://stats.uptimerobot.com/O7N31cA8n)

Python standalone asyncIO API that provides different endpoints to get weather data from winds.mobi mongodb.

Deployed API versions:
- [winds.mobi/api/2/](https://winds.mobi/api/2/) -> rewrite to latest version of 2.x
- [winds.mobi/api/2.3/](https://winds.mobi/api/2.3/)
- [winds.mobi/api/2.2/](https://winds.mobi/api/2.2/) -> deprecated, permanent redirect to 2.3

OpenAPI documentation:
- /doc
- /redoc

## Run the project with docker compose (simple way)
### Dependencies
- [Docker](https://docs.docker.com/get-docker/)

Create an `.env` file from `.env.template` read by docker compose:
- `cp .env.template .env`

Then start the api:
- `docker compose up --build`
- OpenAPI client: http://localhost:8001/doc

## Run the project locally
### Dependencies
- Python 3.11
- [Poetry](https://python-poetry.org)

Create an `.env.localhost` file from `.env.localhost.template` read by `dotenv` for our local commands:
- `cp .env.localhost.template .env.localhost`

### Create python virtual environment and install dependencies
- `poetry install`

### Activate python virtual environment
- `poetry shell`

### Run the server
```
dotenv -f .env.localhost run \
uvicorn --log-config=config/local/logging.yaml --proxy-headers --root-path="$ROOT_PATH" --port 8001 winds_mobi_api.main:app
```
or with opentelemetry instrumentation:
```
dotenv -f .env.localhost run \
opentelemetry-instrument --service_name=winds-mobi-api --metrics_exporter=none \
uvicorn --log-config=config/local/logging.yaml --proxy-headers --root-path="$ROOT_PATH" --port 8001 winds_mobi_api.main:app
```
- OpenAPI client: http://localhost:8001/doc

## Licensing
winds.mobi is licensed under the AGPL License, Version 3.0. See [LICENSE.txt](LICENSE.txt)
