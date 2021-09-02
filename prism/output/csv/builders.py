import logging


def build_csv_lines_export(osm_route_masters, routes_geom, config):
    lines = []
    line_route_mapping = []
    for osm_line in osm_route_masters:
        routes_geom_list = [routes_geom.get(route) for route in osm_line.routes_list]
        lines.append(
            {
                "line_id": osm_line.id,
                "name": osm_line.tags.get("name"),
                "code": osm_line.tags.get("ref"),
                "colour": osm_line.tags.get("colour"),
                "operator": osm_line.tags.get("operator"),
                "network": osm_line.tags.get("network"),
                "mode": osm_line.tags.get("route_master"),
                "frequency": osm_line.tags.get("interval"),
                "opening_hours": osm_line.tags.get("opening_hours"),
                "frequency_exceptions": osm_line.tags.get("interval:conditional"),
                "charge": osm_line.tags.get("charge"),
                "wheelchair": osm_line.tags.get("wheelchair"),
                "shape": create_wkt_multilinestring_from_geom_list(routes_geom_list),
            }
        )
        routes = [
            {"line_id": osm_line.id, "route_id": osm_route}
            for osm_route in osm_line.routes_list
        ]
        line_route_mapping += routes
    return lines, line_route_mapping


def build_csv_routes_export(osm_routes, routes_geom, config):
    routes = []
    route_stop_mapping = []
    for osm_route in osm_routes.values():
        routes.append(
            {
                "route_id": osm_route.id,
                "name": osm_route.tags.get("name"),
                "code": osm_route.tags.get("ref"),
                "destination": osm_route.tags.get("from"),
                "origin": osm_route.tags.get("to"),
                "colour": osm_route.tags.get("colour"),
                "operator": osm_route.tags.get("operator"),
                "network": osm_route.tags.get("network"),
                "mode": osm_route.tags.get("route"),
                "frequency": osm_route.tags.get("interval"),
                "opening_hours": osm_route.tags.get("opening_hours"),
                "frequency_exceptions": osm_route.tags.get("interval:conditional"),
                "travel_time": osm_route.tags.get("duration"),
                "shape": create_wkt_linestring_from_geom(routes_geom.get(osm_route.id)),
            }
        )
        stops = [
            {"route_id": osm_route.id, "stop_point_id": stop_point}
            for stop_point in osm_route.stops_list
        ]
        route_stop_mapping += stops
    return routes, route_stop_mapping


def build_csv_stop_points_export(osm_stops, config):
    for osm_stop in osm_stops.values():
        yield {
            "stop_point_id": osm_stop.id,
            "name": osm_stop.tags.get("name"),
            "latitude": osm_stop.lat,
            "longitude": osm_stop.lon,
            "local_ref": osm_stop.tags.get("local_ref"),
            "wheelchair": osm_stop.tags.get("wheelchair"),
            "shelter": osm_stop.tags.get("shelter"),
        }


def create_wkt_linestring_from_geom(geom):
    if not geom:
        return ""
    latlon_list = ["{} {}".format(latlon.lon, latlon.lat) for latlon in geom]
    latlon_str = ",".join(latlon_list)
    return "LINESTRING({})".format(latlon_str)


def create_wkt_multilinestring_from_geom_list(geom_list):
    routes_geom_list = []
    for geom in geom_list:
        if not geom:
            continue
        latlon_list = ["{} {}".format(latlon.lon, latlon.lat) for latlon in geom]
        latlon_str = ",".join(latlon_list)
        routes_geom_list.append("({})".format(latlon_str))
    routes_str = ",".join(routes_geom_list)
    if not routes_str:
        return ""
    return "MULTILINESTRING({})".format(routes_str)
