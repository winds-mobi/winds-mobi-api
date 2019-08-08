winds.mobi - real-time weather observations
===========================================

[winds.mobi](http://winds.mobi): Paraglider pilot, kitesurfer, check real-time weather conditions of your favorite spots
on your smartphone, your tablet or your computer.

[![Join the chat at https://gitter.im/winds-mobi/winds-mobi-api](https://badges.gitter.im/winds-mobi/winds-mobi-api.svg)](https://gitter.im/winds-mobi/winds-mobi-api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Follow us on https://www.facebook.com/WindsMobi/](https://img.shields.io/badge/facebook-follow_us-blue)](https://www.facebook.com/WindsMobi/)

**Latest version**: [winds.mobi/api/2.2/](https://winds.mobi/api/2.2/doc)  
Deprecated version: ~~[winds.mobi/api/2.1/](https://winds.mobi/api/2.1/doc)~~  
[winds.mobi/api/2/](https://winds.mobi/api/2/doc) -> ~~[winds.mobi/api/2.1/](https://winds.mobi/api/2.1/doc)~~

winds-mobi-api
--------------------

Python 3.7 standalone asyncIO API that provides different endpoints to get weather data from winds.mobi mongodb.

OpenAPI documentation:
- /doc

### Requirements

- python >= 3.7
- mongodb >= 3.0

See [settings.py](https://github.com/winds-mobi/winds-mobi-api/blob/master/settings.py)

### Python environment

- `pipenv install`
- `pipenv shell`

### Run the server

- `uvicorn app:app`

Licensing
---------

Please see the file called [LICENSE.txt](https://github.com/winds-mobi/winds-mobi-api/blob/master/LICENSE.txt)
