import logging
from prism.misc.helpers import crow_fly_distance


def get_geom_for_routes(routes_details, ways_details, stops_details):
    geom = {}
    for osm_route in routes_details.values():
        first_stop_details = None
        if osm_route.stops_list:
            first_stop_details = stops_details.get(osm_route.stops_list[0])
        route_geom = build_geom_from_ways(
            osm_route.id, osm_route.ways_list, ways_details, first_stop_details
        )
        if route_geom:
            geom[osm_route.id] = route_geom
    return geom


def build_geom_from_ways(
    relation_id, ways_list, full_details_of_ways, details_of_first_stop
):
    """Build the geom of the route as a linestring (list of LatLon)"""
    latlon_list = []

    last_roundabout_nodes = []
    for way_id in ways_list:
        current_way = full_details_of_ways.get(way_id)
        if not current_way:
            logging.warning(
                "Missing way {} details (to create shape for {} route)".format(
                    way_id, relation_id
                )
            )
            return

        if len(latlon_list) == 0:
            latlon_list.extend(current_way.points_list)
        elif current_way.points_list[0] == current_way.points_list[-1]:
            # this is a roundabout
            last_roundabout_nodes = current_way.points_list
        elif last_roundabout_nodes:
            roundabout_start_index = last_roundabout_nodes.index(latlon_list[-1])
            if current_way.points_list[0] in last_roundabout_nodes:
                roundabout_end_index = last_roundabout_nodes.index(
                    current_way.points_list[0]
                )
                if roundabout_end_index < roundabout_start_index:
                    del latlon_list[-1]
                    latlon_list.extend(last_roundabout_nodes[roundabout_start_index:-1])
                    latlon_list.extend(last_roundabout_nodes[1:roundabout_end_index])
                else:
                    del latlon_list[-1]
                    latlon_list.extend(
                        last_roundabout_nodes[
                            roundabout_start_index:roundabout_end_index
                        ]
                    )
                latlon_list.extend(current_way.points_list)
            elif current_way.points_list[-1] in last_roundabout_nodes:
                roundabout_end_index = last_roundabout_nodes.index(
                    current_way.points_list[-1]
                )
                if roundabout_end_index < roundabout_start_index:
                    del latlon_list[-1]
                    latlon_list.extend(last_roundabout_nodes[roundabout_start_index:-1])
                    latlon_list.extend(last_roundabout_nodes[1:roundabout_end_index])
                else:
                    del latlon_list[-1]
                    latlon_list.extend(
                        last_roundabout_nodes[
                            roundabout_start_index:roundabout_end_index
                        ]
                    )
                latlon_list.extend(reversed(current_way.points_list))
            else:
                logging.warning(
                    "OSM QA : the geometry of the route {} is not a linestring. Check from {} way".format(
                        relation_id, way_id
                    )
                )
                return
            last_roundabout_nodes = []
        elif latlon_list[-1] == current_way.points_list[0]:
            del latlon_list[-1]
            latlon_list.extend(current_way.points_list)
        elif latlon_list[-1] == current_way.points_list[-1]:
            del latlon_list[-1]
            latlon_list.extend(reversed(current_way.points_list))
        elif latlon_list[0] == current_way.points_list[0]:
            del latlon_list[0]
            latlon_list.reverse()
            latlon_list.extend(current_way.points_list)
        elif latlon_list[0] == current_way.points_list[-1]:
            del latlon_list[0]
            latlon_list.reverse()
            latlon_list.extend(reversed(current_way.points_list))
        else:
            logging.warning(
                "OSM QA : the geometry of the route {} is not a linestring. Check from {} way.".format(
                    relation_id, way_id
                )
            )
            return

    # if only one way in OSM way list, we may need to reverse it
    if len(ways_list) == 1 and details_of_first_stop:
        distance_from_first_geom_point = crow_fly_distance(
            details_of_first_stop.lon,
            details_of_first_stop.lat,
            latlon_list[0].lon,
            latlon_list[0].lat,
        )
        distance_from_last_geom_point = crow_fly_distance(
            details_of_first_stop.lon,
            details_of_first_stop.lat,
            latlon_list[-1].lon,
            latlon_list[-1].lat,
        )
        if distance_from_first_geom_point > distance_from_last_geom_point:
            latlon_list.reverse()

    return latlon_list
