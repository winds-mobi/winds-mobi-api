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
        description='Unix time'
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
    seen: datetime = Schema(
        None,
        description='last time updated (unix time)'
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
