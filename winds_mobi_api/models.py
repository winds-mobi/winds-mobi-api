from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List

from pydantic import BaseModel, Schema


class Status(str, Enum):
    green = 'green'
    orange = 'orange'
    red = 'red'


class Location(BaseModel):
    type: str = Schema(
        'Point',
        description='GeoJSON type'
    )
    coordinates: List[float] = Schema(
        None,
        description='longitude, latitude'
    )


class Pressure(BaseModel):
    qfe: float = Schema(
        ...,
        description='QFE [hPa]'
    )
    qnh: float = Schema(
        ...,
        description='QNH [hPa]'
    )
    qff: float = Schema(
        ...,
        description='QFF [hPa]'
    )


class Measure(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda d: d.timestamp()
        }

    id: datetime = Schema(
        ..., alias='_id',
        description='Last measure [unix timestamp]'
    )
    w_dir: int = Schema(
        None, alias='w-dir',
        description='Wind direction [°](0-359)'
    )
    w_avg: float = Schema(
        None, alias='w-avg',
        description='Wind speed [km/h]'
    )
    w_max: float = Schema(
        None, alias='w-max',
        description='Wind speed max [km/h]'
    )
    temp: float = Schema(
        None,
        description='Temperature [°C]'
    )
    hum: float = Schema(
        None,
        description='Air humidity [%rH]'
    )
    rain: float = Schema(
        None,
        description='Rain [l/m²]'
    )
    pres: Pressure = Schema(
        None,
        description='Air pressure'
    )


class MeasureKey(str, Enum):
    id = '_id'
    w_dir = 'w-dir'
    w_avg = 'w-avg'
    w_max = 'w-max'
    temp = 'temp'
    hum = 'hum'
    rain = 'rain'
    pres = 'pres'


measure_key_defaults = [MeasureKey.id, MeasureKey.w_dir, MeasureKey.w_avg, MeasureKey.w_max, MeasureKey.temp,
                        MeasureKey.hum, MeasureKey.rain, MeasureKey.pres]


class Station(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda d: d.timestamp()
        }

    id: str = Schema(
        ..., alias='_id',
        description='Unique ID {pv-code}-{pv-id} (jdc-1010)'
    )
    pv_id: str = Schema(
        None, alias='pv-id',
        description='Provider ID'
    )
    pv_code: str = Schema(
        None, alias='pv-code',
        description='Provider code (jdc)'
    )
    pv_name: str = Schema(
        None, alias='pv-name',
        description='Provider name (jdc.ch)'
    )
    short: str = Schema(
        None,
        description='Short name'
    )
    name: str = Schema(
        None,
        description='Name'
    )
    alt: int = Schema(
        None,
        description='Altitude [m]'
    )
    peak: bool = Schema(
        None,
        description='Is the station on a peak'
    )
    status: Status = Schema(
        None,
        description='Status'
    )
    tz: str = Schema(
        None,
        description='Timezone (Europe/Zurich)'
    )
    loc: Location = Schema(
        None,
        description='Location [geoJSON point]'
    )
    last: Measure = Schema(
        None,
        description='Last measurement values'
    )
    url: Optional[Dict[str, str]] = Schema(
        None,
        description='Urls to the provider station per language'
    )


class StationKey(str, Enum):
    pv_id = 'pv-id'
    pv_code = 'pv-code'
    pv_name = 'pv-name'
    short = 'short'
    name = 'name'
    alt = 'alt'
    peak = 'peak'
    status = 'status'
    tz = 'tz'
    loc = 'loc'
    url = 'url'
    last_id = 'last._id'
    last_w_dir = 'last.w-dir'
    last_w_avg = 'last.w-avg'
    last_w_max = 'last.w-max'
    last_temp = 'last.temp'
    last_hum = 'last.hum'
    last_rain = 'last.rain'
    last_pres = 'last.pres'


station_key_defaults = [StationKey.pv_code, StationKey.pv_name, StationKey.short, StationKey.name, StationKey.alt,
                        StationKey.peak, StationKey.status, StationKey.tz, StationKey.loc,

                        StationKey.last_id, StationKey.last_w_dir, StationKey.last_w_avg, StationKey.last_w_max,
                        StationKey.last_temp, StationKey.last_hum, StationKey.last_rain, StationKey.last_pres]
