import webcolors
import logging
from math import sqrt

from prism.misc.models import Route
from prism.output.gtfs.builders.agency_builder import get_agency_id

mode_mapping = {
    "tram": 0,
    "light_rail": 0,
    "subway": 1,
    "rail": 2,
    "railway": 2,
    "train": 2,
    "bus": 3,
    "ferry": 4,
}


def build_routes(osm_lines, osm_routes, config):
    use_network_as_agency = config["use_network_as_agency"]

    for osm_line in osm_lines:
        color, txt_color = create_route_colors(osm_line)
        yield Route(
            osm_line.id,
            create_route_short_name(osm_line),
            create_route_long_name(osm_line, osm_routes),
            create_route_type(osm_line),
            create_route_url(osm_line),
            color,
            txt_color,
            get_agency_id(osm_line, config),
        )


def create_route_short_name(osm_line):
    return osm_line.tags.get("ref") or ""


def create_route_type(osm_line):
    osm_mode = osm_line.tags.get("route_master") or "bus"
    return mode_mapping[osm_mode]


def create_route_long_name(osm_line, osm_routes):
    """Create a meaningful route name."""
    name = (
        osm_line.tags.get("name")
        or osm_line.tags.get("alt_name")
        or "OSM Route No. {}".format(osm_line.id)
    )

    # The line name in the OSM data
    # is in the following format:
    # '{transport mode} {route number if any} :
    # {A terminus} ↔ {The other terminus}'
    # But in GTFS, it is good practice not to repeat
    # the route_short_name in the route_long_name,
    # so we use the terminuses from one route to construct
    # another route_long_name if needed

    route_number = osm_line.tags.get("ref")
    if route_number and route_number in name:
        first_osm_route = osm_routes.get(osm_line.routes_list[0])
        if first_osm_route:
            if first_osm_route.tags.get("from") and first_osm_route.tags.get("to"):
                name = "{} ↔ {}".format(
                    first_osm_route.tags.get("from"), first_osm_route.tags.get("to")
                )
            else:
                logging.warning(
                    "OSM QA : Missing origin (from tag) or destination (to tag) on OSM route {}".format(
                        first_osm_route.id
                    )
                )
    return name


def create_route_url(osm_line):
    return "https://jungle-bus.github.io/unroll/route.html?line={}".format(
        osm_line.id[1:]
    )


def create_route_colors(osm_line):
    osm_colour = osm_line.tags.get("colour") or osm_line.tags.get("vehicle:colour")
    if osm_colour:
        try:
            # Check if colour is a valid hex format
            osm_colour = webcolors.normalize_hex(osm_colour)
        except ValueError:
            try:
                # Convert web color names into rgb hex values
                osm_colour = webcolors.name_to_hex(osm_colour)
            except ValueError:
                logging.warning(
                    "OSM QA : Invalid colour: {} found on OSM line {}".format(
                        osm_colour, osm_line.id
                    )
                )
                return ("", "")

        text_colour = "000000"
        # for the text, choose between black and white to maximise contrast
        red, green, blue = (
            int(osm_colour[1:3], 16),
            int(osm_colour[3:5], 16),
            int(osm_colour[5:7], 16),
        )
        brightness = sqrt(
            red * red * 0.241 + green * green * 0.691 + blue * blue * 0.068
        )
        if brightness <= 130:
            text_colour = "ffffff"

        return (osm_colour.strip("#"), text_colour)

    return ("", "")
