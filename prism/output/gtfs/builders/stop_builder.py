import logging

from prism.misc.models import Stop


def build_stops(osm_stops, config):
    default_stop_name = config["default_stop_name"]

    for osm_stop in osm_stops.values():
        yield Stop(
            osm_stop.id,
            osm_stop.tags.get("name") or default_stop_name,
            osm_stop.lon,
            osm_stop.lat,
            create_stop_code(osm_stop),
            create_stop_wheelchair_boarding(osm_stop),
            0,
            "",
        )


def create_stop_wheelchair_boarding(osm_stop):
    """Map wheelchair tag with GTFS wheelchair_boarding."""
    wheelchair_tag = osm_stop.tags.get("wheelchair")
    if not wheelchair_tag:
        return 0
    if wheelchair_tag == "limited":
        return 1
    elif wheelchair_tag == "yes":
        return 1
    elif wheelchair_tag == "no":
        return 2
    else:
        logging.warning(
            "OSM QA : Unknown OSM wheelchair tag {} on {}".format(
                wheelchair_tag, osm_stop.id
            )
        )
        return 0


def create_stop_code(osm_stop):
    ref_tag = osm_stop.tags.get("local_ref")
    if not ref_tag:
        return ""
    return ref_tag
