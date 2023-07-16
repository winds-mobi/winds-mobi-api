winds.mobi - real-time weather observations
===========================================

[![Follow us](https://img.shields.io/badge/facebook-follow_us-blue)](https://www.facebook.com/WindsMobi/)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m783264581-61aa86de256a62e17ec4b862?label=API%202.2)](https://stats.uptimerobot.com/O7N31cA8n)

[winds.mobi](http://winds.mobi): Paraglider pilot, kitesurfer, check real-time weather conditions of your favorite spots
on your smartphone, your tablet or your computer.

winds-mobi-api
--------------------

Python standalone asyncIO API that provides different endpoints to get weather data from winds.mobi mongodb.

Deployed API versions:
- [winds.mobi/api/2.3/](https://winds.mobi/api/2.3/doc)
- [winds.mobi/api/2.2/](https://winds.mobi/api/2.2/doc)
- [winds.mobi/api/2/](https://winds.mobi/api/2/doc) -> 2.2

OpenAPI documentation:
- /doc
- /redoc

### Dependencies

- python 3.11 and [poetry](https://python-poetry.org) 
- mongodb 4.4

### Run the project with docker compose (simple way)

Create a `.env` file from `.env.template` which will be read by docker compose:

Then start the api:

- `docker compose --profile=api up --build`

### Run the project locally on macOS

- `poetry install`

### Run the server

Create a `.env.localhost` file from `.env.localhost.template` which will be read by docker compose:

- `dotenv -f .env.localhost run uvicorn --proxy-headers --root-path /api/2.3 --port 8001 winds_mobi_api.main:app`

Version history
---------------

See [CHANGELOG.md](CHANGELOG.md).

Licensing
---------

See [LICENSE.txt](LICENSE.txt)
