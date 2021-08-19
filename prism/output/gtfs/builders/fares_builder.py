import logging
import re

from prism.output.gtfs.builders.agency_builder import get_agency_id

from prism.misc.models import FareAttributes, FareRule


def build_fares(osm_lines, config):
    use_network_as_agency = config["use_network_as_agency"]

    fare_details = {}
    fare_rules = []

    for osm_line in osm_lines:
        osm_charge = osm_line.tags.get("charge")
        if not osm_charge:
            logging.warning(
                "OSM QA : Missing price (charge tag) on OSM line {}".format(osm_line.id)
            )
            continue

        digits_in_osm_charge = re.findall(r"\d+", osm_charge)
        if digits_in_osm_charge:
            price = float(digits_in_osm_charge[0])
            currency = osm_charge.split(digits_in_osm_charge[0])[-1].replace(" ", "")
        else:
            logging.warning(
                "OSM QA : Cannot extract price and currency from charge tag {} on OSM line {}".format(
                    osm_charge, osm_line.id
                )
            )
            continue

        if osm_charge not in fare_details:
            fare_details[osm_charge] = FareAttributes(
                osm_charge, price, currency, 0, 0, get_agency_id(osm_line, config)
            )

        fare_rules.append(FareRule(osm_charge, osm_line.id))

    return fare_details.values(), fare_rules
