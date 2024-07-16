import logging
from datetime import datetime
from typing import Annotated, List, Union

import numpy as np
import pymongo
from aiocache import cached
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from scipy.stats import linregress
from stop_words import StopWordError, get_stop_words

from winds_mobi_api import diacritics
from winds_mobi_api.database import mongodb
from winds_mobi_api.language import negotiate_language
from winds_mobi_api.models import (
    Measure,
    MeasureKey,
    Station,
    StationKey,
    Status,
    measure_key_defaults,
    station_key_defaults,
)
from winds_mobi_api.mongo_utils import generate_box_geometry
from winds_mobi_api.settings import settings

log = logging.getLogger(__name__)
router = APIRouter()


@cached(ttl=10 * 60)
async def get_collection_names(mongodb):
    return await mongodb.list_collection_names()


@cached(ttl=10 * 60)
async def get_save_clusters(mongodb):
    return await mongodb.stations_clusters.find_one("save_clusters")


def response(data):
    if settings.response_schema_validation:
        return data
    else:
        return ORJSONResponse(data, 200)


error_detail_doc = {"application/json": {"schema": {"type": "object", "properties": {"detail": {"type": "string"}}}}}


@router.get(
    "/stations/{station_id}/",
    status_code=200,
    response_model=Station,
    summary="Get a station",
    response_class=ORJSONResponse,
    description="""
Example:
- Le Suchet: [stations/holfuy-1636](stations/holfuy-1636)
""",  # noqa: E501
    responses={404: {"description": "Station not found", "content": {**error_detail_doc}}},
)
async def get_station(
    mongodb: Annotated[AsyncIOMotorDatabase, Depends(mongodb)],
    station_id: str = Path(..., description="The station ID to request"),
    keys: List[StationKey] = Query(station_key_defaults, description="List of keys to return"),
):
    projection_dict = {}
    for key in keys:
        projection_dict[key.value] = 1
    # last._id should be always returned
    projection_dict["last._id"] = 1

    station = await mongodb.stations.find_one({"_id": station_id}, projection_dict)
    if not station:
        raise HTTPException(status_code=404, detail=f"No station with id '{station_id}'")
    return response(station)


@router.get(
    "/stations/",
    status_code=200,
    response_model=List[Station],
    summary="Search for stations",
    response_class=ORJSONResponse,
    description="""
Examples:
- Get 5 stations from holfuy.com: [stations/?limit=5&provider=holfuy](stations/?limit=5&provider=holfuy)
- Search (ignore accents): [stations/?search=dole](stations/?search=dole)
- Search for 3 stations around Yverdon: [stations/?near-lat=46.78&near-lon=6.63&limit=3](stations/?near-lat=46.78&near-lon=6.63&limit=3)
- Search 20 km around Yverdon: [stations/?near-lat=46.78&near-lon=6.63&near-distance=20000](stations/?near-lat=46.78&near-lon=6.63&near-distance=20000)
- Return holfuy-1636 and holfuy-1293: [stations/?ids=holfuy-1636&ids=holfuy-1293](stations/?ids=holfuy-1636&ids=holfuy-1293)
- Search for 3 working mountain stations that have measures more recent than 1 hour: [stations/?status=green&limit=3&is-peak=true&last-measure=3600](stations/?status=green&limit=3&is-peak=true&last-measure=3600)
""",  # noqa: E501
    responses={
        400: {"description": "Bad request", "content": {**error_detail_doc}},
        404: {"description": "Station not found", "content": {**error_detail_doc}},
    },
)
async def find_stations(
    mongodb: Annotated[AsyncIOMotorDatabase, Depends(mongodb)],
    request_limit: int = Query(20, alias="limit", description="Nb stations to return (max=500)"),
    keys: List[StationKey] = Query(station_key_defaults, description="List of keys to return"),
    provider: str = Query(None, description="Returns only stations of the given provider id. Limit is not enforced"),
    search: str = Query(None, description="String to search (ignoring accent)"),
    search_language: str = Query(
        None, alias="search-language", description="Language of the search. Default to request language or 'en'"
    ),
    near_latitude: float = Query(None, alias="near-lat", description="Geo search near: latitude ie 46.78"),
    near_longitude: float = Query(None, alias="near-lon", description="Geo search near: longitude ie 6.63"),
    near_distance: int = Query(
        None, alias="near-distance", description="Geo search near: distance from lat,lon [meters]"
    ),
    within_pt1_latitude: float = Query(
        None, alias="within-pt1-lat", description="Geo search within rectangle: pt1 latitude"
    ),
    within_pt1_longitude: float = Query(
        None, alias="within-pt1-lon", description="Geo search within rectangle: pt1 longitude"
    ),
    within_pt2_latitude: float = Query(
        None, alias="within-pt2-lat", description="Geo search within rectangle: pt2 latitude"
    ),
    within_pt2_longitude: float = Query(
        None, alias="within-pt2-lon", description="Geo search within rectangle: pt2 longitude"
    ),
    is_peak: bool = Query(
        None, alias="is-peak", description="Return only the stations that are located on top of a peak"
    ),
    status: Status = Query(
        None, description="Return only the stations with the given status: 'green', 'orange' or 'red'"
    ),
    last_measure: Union[int, datetime] = Query(
        None,
        alias="last-measure",
        description="Return only the stations with a measure more recent that {last-measure}. "
        "Can be a duration in seconds or a absolute datetime, for example: 2019-08-16 15:30",
    ),
    is_highest_duplicates_rating: bool = Query(
        None,
        alias="is-highest-duplicates-rating",
        description="Return only stations with the highest duplicates rating (filter stations at the same place)",
    ),
    ids: List[str] = Query(None, description="Returns stations by ids"),
    accept_language: str = Header(None),
):
    if 1 <= request_limit <= 500:
        limit = request_limit
    else:
        limit = 500
    use_limit = True

    projection_dict = {}
    for key in keys:
        projection_dict[key.value] = 1
    # last._id should be always returned
    projection_dict["last._id"] = 1

    now = datetime.now().timestamp()
    query = {"status": {"$ne": "hidden"}, "last._id": {"$gt": now - 30 * 24 * 3600}}

    if provider:
        use_limit = False
        query["pv-code"] = provider

    if search:
        use_limit = True
        if not search_language:
            search_language = negotiate_language(accept_language, default="en")
        try:
            stop_words = get_stop_words(search_language)
        except StopWordError:
            stop_words = get_stop_words("en")

        or_queries = []
        for word in search.split():
            if word not in stop_words:
                regexp_query = diacritics.create_regexp(diacritics.normalize(word))
                or_queries.append({"name": {"$regex": regexp_query, "$options": "i"}})
                or_queries.append({"short": {"$regex": regexp_query, "$options": "i"}})

        if or_queries:
            query["$or"] = or_queries

    if is_peak is not None:
        query["peak"] = {"$eq": is_peak}

    if status is not None:
        query["status"] = {"$eq": status}

    if last_measure is not None:
        timestamp = None
        if isinstance(last_measure, int):
            timestamp = now - last_measure
        elif isinstance(last_measure, datetime):
            timestamp = last_measure.timestamp()
        if timestamp:
            query["last._id"] = {"$gte": int(timestamp)}

    if is_highest_duplicates_rating:
        # Return stations with "duplicates.is_highest_rating" that exists and is True
        # https://www.mongodb.com/docs/v4.4/tutorial/query-for-null-fields/#non-equality-filter
        query["duplicates.is_highest_rating"] = {"$ne": False}

    if near_latitude and near_longitude:
        if near_distance:
            query["loc"] = {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [near_longitude, near_latitude]},
                    "$maxDistance": near_distance,
                }
            }
        else:
            query["loc"] = {"$near": {"$geometry": {"type": "Point", "coordinates": [near_longitude, near_latitude]}}}
        # $near results are already sorted: return now
        cursor = mongodb.stations.find(query, projection_dict).limit(limit)
        return response(await cursor.to_list(None))

    if (
        within_pt1_latitude is not None
        and within_pt1_longitude is not None
        and within_pt2_latitude is not None
        and within_pt2_longitude is not None
    ):
        if within_pt1_latitude == within_pt2_latitude and within_pt1_longitude == within_pt2_longitude:
            # Empty box
            return response([])

        query["loc"] = {
            "$geoWithin": {
                "$geometry": generate_box_geometry(
                    (within_pt2_longitude, within_pt2_latitude), (within_pt1_longitude, within_pt1_latitude)
                )
            }
        }

        def get_cluster_query(cluster: int):
            return {**query, "clusters": {"$elemMatch": {"$lte": cluster}}}

        save_cluster = await get_save_clusters(mongodb)
        cluster_min = save_cluster["min"]
        cluster_max = save_cluster["max"]
        x = [x for x in np.linspace(cluster_min, cluster_max, 3)]
        y = [await mongodb.stations.count_documents(get_cluster_query(int(cluster))) for cluster in x]
        result = linregress(x, y)
        cluster_value = (limit - result.intercept) / result.slope
        cluster_value = max(cluster_value, cluster_min)
        if cluster_value <= cluster_max:
            cluster = int(cluster_value)
        else:
            cluster = None

        if cluster:
            cursor = mongodb.stations.find(get_cluster_query(cluster), projection_dict)
        else:
            cursor = mongodb.stations.find(query, projection_dict)
        stations = await cursor.to_list(None)
        log.debug(f"Result with limit={limit}: cluster {cluster} with {len(stations)} stations")
        return response(stations)

    if ids:
        query["_id"] = {"$in": ids}
        cursor = mongodb.stations.find(query, projection_dict)
        stations = await cursor.to_list(None)
        stations.sort(key=lambda station: ids.index(station["_id"]))
        return response(stations)

    cursor = mongodb.stations.find(query, projection_dict).sort("short", pymongo.ASCENDING)
    if use_limit:
        cursor.limit(limit)
    elif request_limit >= 1:
        cursor.limit(request_limit)
    return response(await cursor.to_list(None))


@router.get(
    "/stations/{station_id}/historic/",
    status_code=200,
    response_model=List[Measure],
    summary="Get historic data for a station since a duration",
    response_class=ORJSONResponse,
    description="""
Example:

- Historic Le Suchet (1 hour): [stations/holfuy-1636/historic/?duration=3600](stations/holfuy-1636/historic/?duration=3600)
""",  # noqa: E501
    responses={
        400: {"description": "Bad request", "content": {**error_detail_doc}},
        404: {"description": "Station not found", "content": {**error_detail_doc}},
    },
)
async def get_station_historic(
    mongodb: Annotated[AsyncIOMotorDatabase, Depends(mongodb)],
    station_id: str = Path(..., description="The station ID to request"),
    duration: int = Query(3600, description="Historic duration"),
    keys: List[MeasureKey] = Query(measure_key_defaults, description="List of keys to return"),
):
    projection_dict = {}
    for key in keys:
        projection_dict[key.value] = 1

    if duration > 7 * 24 * 3600:
        raise HTTPException(status_code=400, detail="Duration > 7 days")

    station = await mongodb.stations.find_one({"_id": station_id})
    if not station:
        raise HTTPException(status_code=404, detail=f"No station with id '{station_id}'")

    if "last" not in station or station_id not in await get_collection_names(
        mongodb=mongodb, aiocache_wait_for_write=False
    ):
        raise HTTPException(status_code=404, detail=f"No historic data for station id '{station_id}'")
    last_time = station["last"]["_id"]
    start_time = last_time - duration
    cursor = mongodb[station_id].find({"_id": {"$gte": start_time}}, projection_dict, sort=(("_id", -1),))
    return response(await cursor.to_list(None))
