import logging

from prism.misc.models import Agency


def build_agencies(osm_lines, config):
    use_network_as_agency = config["use_network_as_agency"]
    default_agency = config["default_agency_to_use"]

    tag_for_agency_name = "operator"
    alt_tag_tag_for_agency_name = "network"

    if use_network_as_agency:
        tag_for_agency_name = "network"
        alt_tag_tag_for_agency_name = "operator"

    agencies = {}

    for osm_line in osm_lines:
        if not osm_line.tags.get(tag_for_agency_name):
            logging.warning(
                "OSM QA : Missing {} on OSM line {}".format(
                    tag_for_agency_name, osm_line.id
                )
            )
            agencies["default_agency"] = default_agency
            continue
        agency_name = osm_line.tags.get(tag_for_agency_name)
        if not agency_name in agencies:
            agencies[agency_name] = Agency(
                agency_name,
                default_agency.agency_url,
                agency_name,
                default_agency.agency_timezone,
                default_agency.agency_lang,
            )
        website = osm_line.tags.get(
            "{}:website".format(tag_for_agency_name)
        ) or osm_line.tags.get("{}:website".format(alt_tag_tag_for_agency_name))
        if website:
            agencies[agency_name] = agencies[agency_name]._replace(agency_url=website)

    for agency in agencies.values():
        yield agency


def get_agency_id(osm_line, config):
    """Get the agency id from tags. Used in other builders to link to the right agency"""
    use_network_as_agency = config["use_network_as_agency"]
    default_agency = config["default_agency_to_use"]

    tag_for_agency_id = "operator"

    if use_network_as_agency:
        tag_for_agency_id = "network"

    if osm_line.tags.get(tag_for_agency_id):
        return osm_line.tags.get(tag_for_agency_id)
    return default_agency.agency_id
