from locust import HttpUser, TaskSet


def find_stations_list(user):
    user.client.get("/stations/?limit=12&near-lat=46.7158569&near-lon=6.6394265")


def find_stations_map(user):
    user.client.get(
        "/stations/?limit=248&within-pt1-lat=47.61494711173539&within-pt1-lon=7.9613777617187225&"
        "within-pt2-lat=45.51162836380102&within-pt2-lon=4.4842049101562225"
    )


def get_station(user):
    user.client.get("/stations/windline-4107")


def get_station_historic(user):
    user.client.get("/stations/windline-4107/historic")


class UserBehavior(TaskSet):
    tasks = {find_stations_list: 2, find_stations_map: 1, get_station: 5, get_station_historic: 1}


class WebsiteUser(HttpUser):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0
