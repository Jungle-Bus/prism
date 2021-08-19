import os
import subprocess

from prism.input.osm.exporter import TransitDataExporter
from prism.output.gtfs.gtfs_writer import GTFSWriter
from prism.misc.config import Configuration


def get_stats_on_osm_extraction(osm_data):
    return {
        "lines_nb": len(osm_data.relations.lines),
        "routes_nb": len(osm_data.relations.routes),
        "stops_nb": len(osm_data.nodes.stops),
        "geom_nb": len(osm_data.geom),
    }


def test_osm_extractor_without_config(osm_transit_data):
    stats = get_stats_on_osm_extraction(osm_transit_data)
    assert stats["lines_nb"] == 7, "Wrong number of extracted OSM lines"
    assert stats["routes_nb"] == 14, "Wrong number of extracted OSM routes"
    assert stats["stops_nb"] == 111, "Wrong number of extracted OSM stops"
    assert stats["geom_nb"] == 12, "Wrong number of extracted OSM route geometries"


def test_osm_extractor_with_config_filter_mode(osm_transit_data_filtered_by_mode):
    stats = get_stats_on_osm_extraction(osm_transit_data_filtered_by_mode)
    assert stats["lines_nb"] == 5, "Wrong number of extracted OSM lines"
    assert stats["routes_nb"] == 10, "Wrong number of extracted OSM routes"
    assert stats["stops_nb"] == 108, "Wrong number of extracted OSM stops"
    assert stats["geom_nb"] == 10, "Wrong number of extracted OSM route geometries"
