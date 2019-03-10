import asyncio
import logging.config
from datetime import datetime
from os import path

import pymongo
import uvloop
import yaml
from aiocache import cached
from motor import motor_asyncio
from quart import Quart, request, jsonify
from quart_cors import cors
from scipy import optimize
from stop_words import get_stop_words, StopWordError, LANGUAGE_MAPPING

import diacritics
from mongo_utils import generate_box_geometry
from settings import LOG_DIR, MONGODB_URL

app = Quart(__name__)
cors(app)

if LOG_DIR:
    with open(path.join(path.dirname(path.abspath(__file__)), 'logging_file.yml')) as f:
        dict = yaml.load(f)
        dict['handlers']['file']['filename'] = path.join(path.expanduser(LOG_DIR), 'winds-mobi-api-data.log')
        logging.config.dictConfig(dict)
else:
    with open(path.join(path.dirname(path.abspath(__file__)), 'logging_console.yml')) as f:
        logging.config.dictConfig(yaml.load(f))

log = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
mongo_db = None


def get_mongo_db():
    global mongo_db

    if not mongo_db:
        mongo_db = motor_asyncio.AsyncIOMotorClient(MONGODB_URL).get_database()
    return mongo_db


@cached(ttl=10 * 60)
async def get_collection_names():
    return await get_mongo_db().list_collection_names()


@app.errorhandler(pymongo.errors.OperationFailure)
def handle_bad_request(e):
    return jsonify({'detail': 'Mongodb error'}), 400


@app.route('/api/2/stations/<station_id>', methods=['GET'], strict_slashes=False)
async def get_station(station_id):
    station = await get_mongo_db().stations.find_one({'_id': station_id})
    if not station:
        return jsonify({'detail': f"No station with id '{station_id}'"}), 404
    return jsonify(station), 200


@app.route('/api/2/stations/', methods=['GET'], strict_slashes=False)
async def find_stations():
    request_limit = int(request.args.get('limit', 20))
    if 1 <= request_limit < 500:
        limit = request_limit
    else:
        limit = 500
    use_limit = True
    provider = request.args.get('provider')
    search = request.args.get('search')
    search_language = request.args.get('search-language')
    near_latitude = request.args.get('near-lat')
    near_longitude = request.args.get('near-lon')
    near_distance = request.args.get('near-distance')
    within_pt1_latitude = request.args.get('within-pt1-lat')
    within_pt1_longitude = request.args.get('within-pt1-lon')
    within_pt2_latitude = request.args.get('within-pt2-lat')
    within_pt2_longitude = request.args.get('within-pt2-lon')
    ids = request.args.getlist('ids', None)

    projections = request.args.getlist('keys', None)
    if projections:
        projection_dict = {}
        for key in projections:
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
            search_language = request.accept_languages.best_match(list(LANGUAGE_MAPPING.keys()), 'en')
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
                        'coordinates': [float(near_longitude), float(near_latitude)]
                    },
                    '$maxDistance': int(near_distance)
                }
            }
        else:
            query['loc'] = {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [float(near_longitude), float(near_latitude)]
                    }
                }
            }
        # $near results are already sorted: return now
        cursor = get_mongo_db().stations.find(query, projection_dict).limit(limit)
        return jsonify(await cursor.to_list(None)), 200

    if within_pt1_latitude and within_pt1_longitude and within_pt2_latitude and within_pt2_longitude:
        if within_pt1_latitude == within_pt2_latitude and within_pt1_longitude == within_pt2_longitude:
            # Empty box
            return jsonify([]), 200

        query['loc'] = {
            '$geoWithin': {
                '$geometry': generate_box_geometry((float(within_pt2_longitude), float(within_pt2_latitude)),
                                                   (float(within_pt1_longitude), float(within_pt1_latitude)))
            }
        }

        now = datetime.now().timestamp()
        nb_stations = await get_mongo_db().stations.count_documents({
            'status': {'$ne': 'hidden'},
            'last._id': {'$gt': now - 30 * 24 * 3600}
        })

        def get_cluster_query(no_cluster):
            cluster_query = query.copy()
            cluster_query['clusters'] = {'$elemMatch': {'$lte': int(no_cluster)}}
            return cluster_query

        async def count(x):
            y = await get_mongo_db().stations.count_documents(get_cluster_query(x))
            return y - limit

        try:
            no_cluster = optimize.brentq(count, 1, nb_stations, maxiter=2, disp=False)
        except ValueError:
            no_cluster = None

        if no_cluster:
            cursor = get_mongo_db().stations.find(get_cluster_query(no_cluster), projection_dict)
            stations = await cursor.to_list(None)
            log.debug(f'limit={limit}, no_cluster={no_cluster:.0f} => {len(stations)}')
        else:
            cursor = get_mongo_db().stations.find(query, projection_dict)
            stations = await cursor.to_list(None)
            log.debug(f'limit={limit} => {len(stations)}')
        return jsonify(stations), 200

    if ids:
        query['_id'] = {'$in': ids}
        cursor = get_mongo_db().stations.find(query, projection_dict)
        stations = await cursor.to_list(None)
        stations.sort(key=lambda station: ids.index(station['_id']))
        return jsonify(stations), 200

    cursor = get_mongo_db().stations.find(query, projection_dict).sort('short', pymongo.ASCENDING)
    if use_limit:
        cursor.limit(limit)
    elif request_limit >= 1:
        cursor.limit(request_limit)
    return jsonify(await cursor.to_list(None)), 200


@app.route('/api/2/stations/<station_id>/historic', methods=['GET'], strict_slashes=False)
async def get_station_historic(station_id):
    log.warning('historic')

    duration = int(request.args.get('duration', 3600))

    projections = request.args.getlist('keys', None)
    if projections:
        projection_dict = {}
        for key in projections:
            projection_dict[key] = 1
    else:
        projection_dict = None

    if duration > 7 * 24 * 3600:
        return jsonify({'detail': 'Duration > 7 days'}), 400

    station = await get_mongo_db().stations.find_one({'_id': station_id})
    if not station:
        return jsonify({'detail': f"No station with id '{station_id}'"}), 404

    if 'last' not in station or station_id not in await get_collection_names():
        return jsonify({'detail': f"No historic data for station id '{station_id}'"}), 404
    last_time = station['last']['_id']
    start_time = last_time - duration
    nb_data = await get_mongo_db()[station_id].count_documents({'_id': {'$gte': start_time}}) + 1
    cursor = get_mongo_db()[station_id].find({}, projection_dict, sort=(('_id', -1),)).limit(nb_data)
    return jsonify(await cursor.to_list(None)), 200


app.run()
