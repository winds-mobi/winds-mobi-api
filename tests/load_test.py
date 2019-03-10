from locust import HttpLocust, TaskSet


def find_stations(l):
    l.client.get('/api/2/stations/?near-lat=46.7158397&near-lon=6.6394218&limit=100')


def get_station(l):
    l.client.get('/api/2/stations/windline-4107/')


def get_station_historic(l):
    l.client.get('/api/2/stations/windline-4107/historic/')


class UserBehavior(TaskSet):
    tasks = {find_stations: 2, get_station: 10, get_station_historic: 1}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0
