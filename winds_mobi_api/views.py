import asyncio
import logging
from datetime import datetime
from typing import List

import pymongo
from aiocache import cached
from fastapi import HTTPException, Path, Query, Header
from scipy import optimize
from starlette.responses import JSONResponse
from stop_words import get_stop_words, StopWordError

from app import app, mongodb, mongodb_sync
from winds_mobi_api import diacritics
from winds_mobi_api.language import negotiate_language
from winds_mobi_api.models import Station, Measure
from winds_mobi_api.mongo_utils import generate_box_geometry

log = logging.getLogger(__name__)
response_validation = False


@cached(ttl=10 * 60)
async def get_collection_names():
    return await mongodb().list_collection_names()


def response(data):
    if response_validation:
        return data
    else:
        return JSONResponse(data, 200)


error_detail_doc = {
    'application/json': {
        'schema': {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string'
                }
            }
        }
    }
}


@app.get(
    '/stations/{station_id}/',
    status_code=200,
    response_model=Station,
    description='''
Get a station

Example:
- Mauborget: [/stations/jdc-1001](/stations/jdc-1001)
''',  # noqa
    responses={
        404: {
            'description': 'Station not found',
            'content': {
                **error_detail_doc
            }
        }
    }
)
async def get_station(
        station_id: str = Path(
            ...,
            description='The station ID to request')
):
    station = await mongodb().stations.find_one({'_id': station_id})
    if not station:
        raise HTTPException(status_code=404, detail=f"No station with id '{station_id}'")
    return response(station)


@app.get(
    '/stations/',
    status_code=200,
    response_model=List[Station],
    description='''
Search for stations

Examples:
- Get 5 stations from jdc.ch: [/stations/?limit=5&provider=jdc](/stations/?limit=5&provider=jdc)
- Search (ignore accents): [/stations/?search=dole](/stations/?search=dole)
- Search for 3 stations around Yverdon: [/stations/?near-lat=46.78&near-lon=6.63&limit=3](/stations/?near-lat=46.78&near-lon=6.63&limit=3)
- Search 20 km around Yverdon: [/stations/?near-lat=46.78&near-lon=6.63&near-distance=20000](/stations/?near-lat=46.78&near-lon=6.63&near-distance=20000)
- Return jdc-1001 and jdc-1002: [/stations/?ids=jdc-1001&ids=jdc-1002](/stations/?ids=jdc-1001&ids=jdc-1002)
''',  # noqa
    responses={
        400: {
            'description': 'Bad request',
            'content': {
                **error_detail_doc
            }
        },
        404: {
            'description': 'Station not found',
            'content': {
                **error_detail_doc
            }
        }
    }
)
async def find_stations(
        request_limit: int = Query(
            20, alias='limit',
            description='Nb stations to return (max=500)'),
        provider: str = Query(
            None,
            description='Returns only stations of the given provider'),
        search: str = Query(
            None, description='String to search (ignoring accent)'),
        keys: List[str] = Query(
            None, description='List of keys to return'),
        search_language: str = Query(
            None, alias='search-language',
            description="Language of the search. Default to request language or 'en'"),
        near_latitude: float = Query(
            None, alias='near-lat',
            description='Geo search near: latitude ie 46.78'),
        near_longitude: float = Query(
            None, alias='near-lon',
            description='Geo search near: longitude ie 6.63'),
        near_distance: int = Query(
            None, alias='near-distance',
            description='Geo search near: distance from lat,lon [meters]'),
        within_pt1_latitude: float = Query(
            None, alias='within-pt1-lat',
            description='Geo search within rectangle: pt1 latitude'),
        within_pt1_longitude: float = Query(
            None, alias='within-pt1-lon',
            description='Geo search within rectangle: pt1 longitude'),
        within_pt2_latitude: float = Query(
            None, alias='within-pt2-lat',
            description='Geo search within rectangle: pt2 latitude'),
        within_pt2_longitude: float = Query(
            None, alias='within-pt2-lon',
            description='Geo search within rectangle: pt2 longitude'),
        ids: List[str] = Query(
            None,
            description='Returns stations by ids'),
        accept_language: str = Header(None)
):
    if 1 <= request_limit <= 500:
        limit = request_limit
    else:
        limit = 500
    use_limit = True

    if keys:
        projection_dict = {}
        for key in keys:
            projection_dict[key] = 1
    else:
        projection_dict = None

    now = datetime.now().timestamp()
    query = {
        'status': {'$ne': 'hidden'},
        'last._id': {'$gt': now - 30 * 24 * 3600}
    }

    if provider:
        use_limit = False
        query['pv-code'] = provider

    if search:
        use_limit = True
        if not search_language:
            search_language = negotiate_language(accept_language, default='en')
        try:
            stop_words = get_stop_words(search_language)
        except StopWordError:
            stop_words = get_stop_words('en')

        or_queries = []
        for word in search.split():
            if word not in stop_words:
                regexp_query = diacritics.create_regexp(diacritics.normalize(word))
                or_queries.append({'name': {'$regex': regexp_query, '$options': 'i'}})
                or_queries.append({'short': {'$regex': regexp_query, '$options': 'i'}})

        if or_queries:
            query['$or'] = or_queries

    if near_latitude and near_longitude:
        if near_distance:
            query['loc'] = {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [near_longitude, near_latitude]
                    },
                    '$maxDistance': near_distance
                }
            }
        else:
            query['loc'] = {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [near_longitude, near_latitude]
                    }
                }
            }
        # $near results are already sorted: return now
        cursor = mongodb().stations.find(query, projection_dict).limit(limit)
        return response(await cursor.to_list(None))

    if within_pt1_latitude and within_pt1_longitude and within_pt2_latitude and within_pt2_longitude:
        if within_pt1_latitude == within_pt2_latitude and within_pt1_longitude == within_pt2_longitude:
            # Empty box
            return response([])

        query['loc'] = {
            '$geoWithin': {
                '$geometry': generate_box_geometry((within_pt2_longitude, within_pt2_latitude),
                                                   (within_pt1_longitude, within_pt1_latitude))
            }
        }

        now = datetime.now().timestamp()
        nb_stations = await mongodb().stations.count_documents({
            'status': {'$ne': 'hidden'},
            'last._id': {'$gt': now - 30 * 24 * 3600}
        })

        def get_cluster_query(no_cluster):
            cluster_query = query.copy()
            cluster_query['clusters'] = {'$elemMatch': {'$lte': int(no_cluster)}}
            return cluster_query

        def count(x):
            y = mongodb_sync().stations.count(get_cluster_query(x))
            return y - limit

        def no_cluster_task():
            return optimize.brentq(count, 1, nb_stations, maxiter=2, disp=False)

        try:
            # CPU an IO bound task using a sync library: executing it in a separated thread to not block the event loop
            no_cluster = await asyncio.get_running_loop().run_in_executor(None, no_cluster_task)
        except ValueError:
            no_cluster = None

        if no_cluster:
            cursor = mongodb().stations.find(get_cluster_query(no_cluster), projection_dict)
            stations = await cursor.to_list(None)
            log.debug(f'limit={limit}, no_cluster={no_cluster:.0f} => {len(stations)}')
        else:
            cursor = mongodb().stations.find(query, projection_dict)
            stations = await cursor.to_list(None)
            log.debug(f'limit={limit} => {len(stations)}')
        return response(stations)

    if ids:
        query['_id'] = {'$in': ids}
        cursor = mongodb().stations.find(query, projection_dict)
        stations = await cursor.to_list(None)
        stations.sort(key=lambda station: ids.index(station['_id']))
        return response(stations)

    cursor = mongodb().stations.find(query, projection_dict).sort('short', pymongo.ASCENDING)
    if use_limit:
        cursor.limit(limit)
    elif request_limit >= 1:
        cursor.limit(request_limit)
    return response(await cursor.to_list(None))


@app.get(
    '/stations/{station_id}/historic/',
    status_code=200,
    response_model=List[Measure],
    description='''
Get historic data for a station since a duration

Example:

- Historic Mauborget (1 hour): [/stations/jdc-1001/historic/?duration=3600](/stations/jdc-1001/historic/?duration=3600)
''',  # noqa
    responses={
        400: {
            'description': 'Bad request',
            'content': {
                **error_detail_doc
            }
        },
        404: {
            'description': 'Station not found',
            'content': {
                **error_detail_doc
            }
        }
    }
)
async def get_station_historic(
        station_id: str = Path(
            ...,
            description='The station ID to request'),
        duration: int = Query(
            3600,
            description='Historic duration'),
        keys: List[str] = Query(
            None, description='List of keys to return')
):
    if keys:
        projection_dict = {}
        for key in keys:
            projection_dict[key] = 1
    else:
        projection_dict = None

    if duration > 7 * 24 * 3600:
        raise HTTPException(status_code=400, detail='Duration > 7 days')

    station = await mongodb().stations.find_one({'_id': station_id})
    if not station:
        raise HTTPException(status_code=404, detail=f"No station with id '{station_id}'")

    if 'last' not in station or station_id not in await get_collection_names():
        raise HTTPException(status_code=404, detail=f"No historic data for station id '{station_id}'")
    last_time = station['last']['_id']
    start_time = last_time - duration
    nb_data = await mongodb()[station_id].count_documents({'_id': {'$gte': start_time}}) + 1
    cursor = mongodb()[station_id].find({}, projection_dict, sort=(('_id', -1),)).limit(nb_data)
    return response(await cursor.to_list(None))
