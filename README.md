winds.mobi - real-time weather observations
===========================================

[winds.mobi](http://winds.mobi): Paraglider pilot, kitesurfer, check real-time weather conditions of your favorite spots
on your smartphone, your tablet or your computer.

Follow this project on:
- [Facebook](https://www.facebook.com/WindsMobi/)

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
