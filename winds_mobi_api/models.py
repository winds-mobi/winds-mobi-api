from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class Status(str, Enum):
    green = "green"
    orange = "orange"
    red = "red"


class Location(BaseModel):
    type: str = Field("Point", title="Type", description="GeoJSON type")
    coordinates: List[float] = Field(None, title="Coordinates", description="longitude, latitude")


class Pressure(BaseModel):
    qfe: float | None = Field(None, title="QFE", description="QFE [hPa]")
    qnh: float | None = Field(None, title="QNH", description="QNH [hPa]")
    qff: float | None = Field(None, title="QFF", description="QFF [hPa]")


class Measure(BaseModel):
    class Config:
        json_encoders = {datetime: lambda d: d.timestamp()}

    id: int = Field(..., alias="_id", title="_ID", description="Measure date [unix timestamp]", example=1565722207)
    w_dir: int = Field(None, alias="w-dir", title="Wind direction", description="Wind direction [°] (0-359)")
    w_avg: float = Field(None, alias="w-avg", title="Wind average", description="Wind speed [km/h]")
    w_max: float = Field(None, alias="w-max", title="Wind max", description="Wind speed max [km/h]")
    temp: float = Field(None, title="Temperature", description="Temperature [°C]")
    hum: float = Field(None, title="Humidity", description="Air humidity [%rH]")
    rain: float = Field(None, title="Rain", description="Rain [l/m²]")
    pres: Pressure = Field(None, title="Pressure", description="Air pressure")


class MeasureKey(str, Enum):
    id = "_id"
    w_dir = "w-dir"
    w_avg = "w-avg"
    w_max = "w-max"
    temp = "temp"
    hum = "hum"
    rain = "rain"
    pres = "pres"


measure_key_defaults = [
    MeasureKey.id,
    MeasureKey.w_dir,
    MeasureKey.w_avg,
    MeasureKey.w_max,
    MeasureKey.temp,
    MeasureKey.hum,
    MeasureKey.rain,
    MeasureKey.pres,
]


class Station(BaseModel):
    class Config:
        json_encoders = {datetime: lambda d: d.timestamp()}

    id: str = Field(..., alias="_id", title="_ID", description="Station ID {pv-code}-{pv-id}, example: jdc-1010")
    pv_id: str = Field(
        None, alias="pv-id", title="Provider ID", description="Station ID in provider space, example: 1010"
    )
    pv_code: str = Field(None, alias="pv-code", title="Provider code", description="Example: jdc")
    pv_name: str = Field(
        None, alias="pv-name", title="Provider name", description="Full provider name, example: jdc.ch"
    )
    short: str = Field(None, title="Short name", description="Short name of the station")
    name: str = Field(None, title="Name", description="Full name of the station")
    alt: int = Field(None, title="Altitude", description="Altitude [m]")
    peak: bool = Field(None, title="Peak", description="Is the station on a peak")
    status: Status = Field(
        None,
        title="Status",
        description="green: station ok, orange: data might be inaccurate, red: station isn't working",
    )
    tz: str = Field(None, title="Timezone", description="Timezone, example: Europe/Zurich")
    loc: Location = Field(None, title="Location", description="Location [geoJSON point]")
    last: Measure = Field(None, title="Last measure", description="Last measurement values")
    url: Dict[str, str] = Field(
        None,
        title="Provider urls",
        description="""Urls to the provider station per language. Example:
```
{
    'default': 'https://provider.com/path/to/station?lang=en',
    'en': 'https://provider.com/path/to/station?lang=en',
    'fr': 'https://provider.com/path/to/station?lang=fr'
}
```""",
    )


class StationKey(str, Enum):
    pv_id = "pv-id"
    pv_code = "pv-code"
    pv_name = "pv-name"
    short = "short"
    name = "name"
    alt = "alt"
    peak = "peak"
    status = "status"
    tz = "tz"
    loc = "loc"
    url = "url"
    last_id = "last._id"
    last_w_dir = "last.w-dir"
    last_w_avg = "last.w-avg"
    last_w_max = "last.w-max"
    last_temp = "last.temp"
    last_hum = "last.hum"
    last_rain = "last.rain"
    last_pres = "last.pres"


station_key_defaults = [
    StationKey.pv_name,
    StationKey.short,
    StationKey.name,
    StationKey.alt,
    StationKey.peak,
    StationKey.status,
    StationKey.tz,
    StationKey.loc,
    StationKey.last_id,
    StationKey.last_w_dir,
    StationKey.last_w_avg,
    StationKey.last_w_max,
    StationKey.last_temp,
    StationKey.last_hum,
    StationKey.last_rain,
    StationKey.last_pres,
]
