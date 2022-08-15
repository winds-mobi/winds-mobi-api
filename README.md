winds.mobi - real-time weather observations
===========================================

[![Follow us on https://www.facebook.com/WindsMobi/](https://img.shields.io/badge/facebook-follow_us-blue)](https://www.facebook.com/WindsMobi/)
[![Uptime https://status.winds.mobi/](https://img.shields.io/uptimerobot/ratio/m783264581-61aa86de256a62e17ec4b862?label=API%202.2)](https://status.winds.mobi/)

[winds.mobi](http://winds.mobi): Paraglider pilot, kitesurfer, check real-time weather conditions of your favorite spots
on your smartphone, your tablet or your computer.

winds-mobi-api
--------------------

Python standalone asyncIO API that provides different endpoints to get weather data from winds.mobi mongodb.

Deployed API versions:
- [winds.mobi/api/2.2/](https://winds.mobi/api/2.2/doc) (**latest**)
- [winds.mobi/api/2/](https://winds.mobi/api/2/doc) -> latest version

OpenAPI documentation:
- /doc
- /redoc

### Requirements

- python >= 3.7
- mongodb >= 3.0

See [settings.py](settings.py)

### Python environment

- `pipenv install`
- `pipenv shell`

### Run the server

- `uvicorn winds_mobi_api.main:app`

Version history
---------------

See [CHANGELOG.md](CHANGELOG.md).

Licensing
---------

See [LICENSE.txt](LICENSE.txt)
