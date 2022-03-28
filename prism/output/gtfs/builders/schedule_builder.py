import logging
import collections

import transporthours
from datetime import timedelta, datetime
from math import cos, sin, atan2, sqrt, radians
from collections import defaultdict

from prism.misc.models import GTFSSchedule
from prism.misc.helpers import crow_fly_distance


_DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
_DEFAULT_SCHEDULE = {"opening_hours": "Mo-Su,PH 05:00-22:00", "interval": "01:00"}
_DAY_ABBREVIATIONS = {
    "monday": "Mo",
    "tuesday": "Tu",
    "wednesday": "We",
    "thursday": "Th",
    "friday": "Fr",
    "saturday": "Sa",
    "sunday": "Su",
}


def build_schedules(osm_lines, osm_routes, osm_stops, osm_geom, config):

    services = {}
    trips = {}
    frequencies = []
    stop_times = []

    transport_hours = transporthours.main.Main()

    departures_by_route_id = config["enumerate_trips"]["departures_by_route_id"]

    for line in osm_lines:

        for route_index, route_id in enumerate(line.routes_list):
            route = osm_routes.get(route_id)

            if not route:
                continue

            if route_id in departures_by_route_id:
                logging.debug(
                    "Departures used to enumerate trips for route {}".format(route_id)
                )

                default_service = {
                    "service_id": "default",
                    "monday": 1,
                    "tuesday": 1,
                    "wednesday": 1,
                    "thursday": 1,
                    "friday": 1,
                    "saturday": 1,
                    "sunday": 1,
                    "start_date": config["feed_info_to_use"]["feed_start_date"],
                    "end_date": config["feed_info_to_use"]["feed_end_date"],
                }
                if "default" not in services:
                    services["default"] = default_service

                for departure_index, departure_detail in enumerate(
                    departures_by_route_id[route_id]
                ):
                    trip_id = "{}#{}".format(route_id, departure_index)
                    shape_id = ""
                    if route_id in osm_geom:
                        shape_id = route_id
                    trips[trip_id] = {
                        "route_id": line.id,
                        "service_id": "default",
                        "shape_id": shape_id,
                        "trip_id": trip_id,
                        "direction_id": route_index % 2,
                        "trip_headsign": route.tags.get("to") or "",
                    }

                    first_index = None
                    last_index = None
                    if departure_detail["first_stop_index"]:
                        first_index = int(departure_detail["first_stop_index"])
                    if departure_detail["last_stop_index"]:
                        last_index = int(departure_detail["last_stop_index"])

                    stop_times += create_gtfs_stop_times_for_a_route(
                        route,
                        osm_stops,
                        trip_id,
                        departure_detail["departure"],
                        config,
                        a_route_stop_first_index=first_index,
                        a_route_stop_last_index=last_index,
                    )

            else:
                write_frequencies = True

                opening_hours = route.tags.get("opening_hours") or line.tags.get(
                    "opening_hours"
                )
                if not opening_hours:
                    opening_hours = _DEFAULT_SCHEDULE["opening_hours"]
                    logging.warning(
                        "OSM QA : Missing opening_hours on OSM line {} or OSM route {}".format(
                            line.id, route.id
                        )
                    )

                interval = (
                    route.tags.get("interval")
                    or line.tags.get("interval")
                    or line.tags.get("frequency")
                )
                if not interval:
                    interval = _DEFAULT_SCHEDULE["interval"]
                    logging.warning(
                        "OSM QA : Missing frequency (interval tag) on OSM line {} or OSM route {}".format(
                            line.id, route.id
                        )
                    )
                    if not config["enumerate_trips"]["use_default_interval_if_empty"]:
                        write_frequencies = False

                if write_frequencies:
                    logging.debug(
                        "Frequencies from OSM used to enumerate trips for route {}".format(
                            route_id
                        )
                    )
                else:
                    logging.debug(
                        "Will only generate one trip for route {}".format(route_id)
                    )

                interval_conditional = (
                    route.tags.get("interval:conditional")
                    or line.tags.get("interval:conditional")
                    or ""
                )

                route_hours_list = transport_hours.tagsToGtfs(
                    {
                        "opening_hours": opening_hours,
                        "interval": interval,
                        "interval:conditional": interval_conditional,
                    }
                )

                route_hours_dict = group_hours_by_service_period(route_hours_list)

                for service_id, route_hours in route_hours_dict.items():
                    trip_id = "{}_{}".format(route_id, service_id)
                    shape_id = ""
                    if route_id in osm_geom:
                        shape_id = route_id
                    trips[trip_id] = {
                        "route_id": line.id,
                        "service_id": service_id,
                        "shape_id": shape_id,
                        "trip_id": trip_id,
                        "direction_id": route_index % 2,
                        "trip_headsign": route.tags.get("to") or "",
                    }

                    if not service_id in services:
                        services[service_id] = {
                            "service_id": service_id,
                            "monday": int(route_hours[0]["monday"]),
                            "tuesday": int(route_hours[0]["tuesday"]),
                            "wednesday": int(route_hours[0]["wednesday"]),
                            "thursday": int(route_hours[0]["thursday"]),
                            "friday": int(route_hours[0]["friday"]),
                            "saturday": int(route_hours[0]["saturday"]),
                            "sunday": int(route_hours[0]["sunday"]),
                            "start_date": config["feed_info_to_use"]["feed_start_date"],
                            "end_date": config["feed_info_to_use"]["feed_end_date"],
                        }

                    if write_frequencies:
                        for route_hour in route_hours:
                            frequencies.append(
                                {
                                    "trip_id": trip_id,
                                    "start_time": route_hour["start_time"],
                                    "end_time": route_hour["end_time"],
                                    "headway_secs": route_hour["headway"],
                                }
                            )

                    stop_times += create_gtfs_stop_times_for_a_route(
                        route, osm_stops, trip_id, None, config
                    )

    return GTFSSchedule(services.values(), stop_times, trips.values(), frequencies)


def create_gtfs_stop_times_for_a_route(
    a_route,
    stop_list,
    trip_id,
    departure_time,
    config,
    a_route_stop_first_index=None,
    a_route_stop_last_index=None,
):
    """
    Create GTFS stop_times by computing duration between each stop inside the route
    according to the algo specified in config
    """

    stop_times = []

    # Make sure that we already know all stops in a_route
    a_route_stops_list = [elem for elem in a_route.stops_list if elem in stop_list]
    if len(a_route.stops_list) != len(a_route_stops_list):
        logging.warning(
            "Missing some nodes details in OSM data (to create schedule for {} route)".format(
                a_route.id
            )
        )
    if a_route_stop_first_index:
        a_route_stops_list = a_route_stops_list[a_route_stop_first_index - 1 :]
    elif a_route_stop_last_index:
        a_route_stops_list = a_route_stops_list[0:a_route_stop_last_index]

    distances_list = get_distances_between_all_stops(a_route_stops_list, stop_list)
    speed = get_default_speed_for_route(a_route, config) * 1000 / 60  # meters / min
    if config["make_stop_times"]["algo"] == "osm_duration_tag":
        trip_duration = get_trip_duration(a_route)
        if not trip_duration:
            logging.debug(
                "Missing trip duration on route {}, will use default speed".format(
                    a_route.id
                )
            )
        else:
            total_distance = sum(distances_list)
            speed = total_distance / trip_duration  # meters / minute
            logging.debug(
                "Computed speed for route {}: ~ {} km/h".format(
                    a_route.id, round(speed * 60 / 1000)
                )
            )

    durations_list = [
        distance_between_two_stops / speed
        for distance_between_two_stops in distances_list
    ]

    departure_time = departure_time or datetime(1991, 1, 29, 6, 0, 0)
    first_departure_of_trip = departure_time
    for stop_index, stop_id in enumerate(a_route_stops_list):
        stop = stop_list.get(stop_id)

        stop_time = {
            "trip_id": trip_id,
            "stop_id": stop_id,
            "stop_sequence": stop_index,
            "timepoint": 0,
        }

        if stop_index == 0:
            _time = departure_time.strftime("%H:%M:%S")
            stop_time["departure_time"] = _time
            stop_time["arrival_time"] = _time
        else:
            duration = durations_list[stop_index - 1]
            departure_time += timedelta(minutes=duration)
            _time = departure_time.strftime("%H:%M:%S")
            stop_time["departure_time"] = _time
            stop_time["arrival_time"] = _time
            if (
                departure_time.day != first_departure_of_trip.day
            ):  # after midnight times needs to be greater than 24:MM:SS
                stop_time["departure_time"] = "{}:{:02d}:{:02d}".format(
                    departure_time.hour + 24,
                    departure_time.minute,
                    departure_time.second,
                )
                stop_time["arrival_time"] = stop_time["departure_time"]

        stop_times.append(stop_time)
    return stop_times


def get_distances_between_all_stops(stop_ids_list, stop_list):
    distances = []
    for stop_index in range(len(stop_ids_list) - 1):
        first_stop_id = stop_ids_list[stop_index]
        second_stop_id = stop_ids_list[stop_index + 1]

        first_stop = stop_list[first_stop_id]
        second_stop = stop_list[second_stop_id]

        distance_between_stops = crow_fly_distance(
            first_stop.lon, first_stop.lat, second_stop.lon, second_stop.lat
        )
        distances.append(distance_between_stops)
    return distances


def get_default_speed_for_route(a_route, config):
    current_mode = a_route.tags["route"] or "bus"
    return config["make_stop_times"]["speed_by_mode"][current_mode]


def get_trip_duration(a_route):
    if "duration" in a_route.tags:
        try:
            travel_time = int(a_route.tags["duration"])
            if not travel_time > 0:
                logging.warning(
                    "OSM QA : Invalid travel duration {} found on OSM line {}".format(
                        travel_time, a_route.id
                    )
                )
                return
        except (ValueError, TypeError) as e:
            logging.warning(
                "OSM QA : Invalid travel duration {} found on OSM line {} (should be a number)".format(
                    a_route.tags["duration"], a_route.id
                )
            )
            return
    else:
        logging.warning(
            "OSM QA : Missing travel duration (duration tag) on OSM route {}".format(
                a_route.id
            )
        )
        return
    return travel_time


def group_hours_by_service_period(transport_hours_list):
    transport_hours_dict = {}
    for hour in transport_hours_list:
        service_id = get_service_id_from_transport_hour(hour)

        if service_id in transport_hours_dict.keys():
            transport_hours_dict[service_id].append(hour)
        else:
            transport_hours_dict[service_id] = [hour]

    return transport_hours_dict


def get_service_id_from_transport_hour(a_transport_hour):
    # TODO : should be part of transporthours lib ?
    service_days = [
        day_name
        for day_name in _DAYS_OF_WEEK
        if day_name in a_transport_hour and a_transport_hour[day_name]
    ]

    if not service_days:
        logging.warning("Transport_hour missing service days. Assuming 7 days a week.")
        service_days = _DAYS_OF_WEEK

    def date_range(start, end):
        return _DAY_ABBREVIATIONS[start] + "-" + _DAY_ABBREVIATIONS[end]

    if collections.Counter(service_days) == collections.Counter(_DAYS_OF_WEEK):
        return date_range("monday", "sunday")
    if collections.Counter(service_days) == collections.Counter(_DAYS_OF_WEEK[:5]):
        return date_range("monday", "friday")
    if collections.Counter(service_days) == collections.Counter(_DAYS_OF_WEEK[:6]):
        return date_range("monday", "saturday")
    if collections.Counter(service_days) == collections.Counter(_DAYS_OF_WEEK[-2:]):
        return date_range("saturday", "sunday")

    return ",".join([_DAY_ABBREVIATIONS[day_name] for day_name in service_days])
