import math

LAT = 1
LNG = 0
PRECISION = 1.0  # In degrees latitude


def additional_points_needed(lat, lon1, lon2):
    """
    Calculates how many extra equdistant points are needed along an East-West path to achieve the given precision.
    """
    x = lat * math.pi / 180
    y = (lon1 - lon2) * math.pi / 360
    n = 0
    delta = 361

    while delta > PRECISION:
        n += 1
        lat_max = math.atan(math.tan(x) / math.cos(y / n)) * 180 / math.pi
        delta = abs(lat_max - lat)

    return int(math.ceil(math.pow(2, n - 1) - 1))


def generate_box_geometry(sw, ne):
    """
    generate_box_geometry will generate a `Polygon` type bounding geometry for use on 2DSphere indices
    that approximates a flat $box query. It takes in the south-west and north-east corner of the box.
    http://map.visualzhou.com/
    """

    points_bottom = additional_points_needed(sw[LAT], sw[LNG], ne[LNG])
    points_top = additional_points_needed(ne[LAT], sw[LNG], ne[LNG])

    coordinates = []

    for i in range(0, points_bottom + 2):
        lon = sw[LNG] + (i / (points_bottom + 1)) * (ne[LNG] - sw[LNG])
        coordinates.append([lon, sw[LAT]])

    for j in range(0, points_top + 2):
        lon = ne[LNG] - (j / (points_top + 1)) * (ne[LNG] - sw[LNG])
        coordinates.append([lon, ne[LAT]])

    coordinates.append(sw)

    return {
        'type': 'Polygon',
        'coordinates': [coordinates],
        # Resolves "Big polygon" issue, requires mongodb 3.x
        # http://docs.mongodb.org/manual/reference/operator/query/geometry/#op._S_geometry
        'crs': {
            'type': 'name',
            'properties': {'name': 'urn:x-mongodb:crs:strictwinding:EPSG:4326'}
        }
    }
