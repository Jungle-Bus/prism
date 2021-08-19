import logging


def get_geom_for_routes(routes_details, ways_details):
    geom = {}
    for osm_route in routes_details.values():
        route_geom = build_geom_from_ways(
            osm_route.id, osm_route.ways_list, ways_details
        )
        if route_geom:
            geom[osm_route.id] = route_geom
    return geom


def build_geom_from_ways(relation_id, ways_list, full_details_of_ways):
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
            if current_way.points_list[0] in last_roundabout_nodes:
                latlon_list.extend(current_way.points_list)
            elif current_way.points_list[-1] in last_roundabout_nodes:
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

    return latlon_list
