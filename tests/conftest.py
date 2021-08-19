"""Reusable fixtures used by the tests"""
import pathlib
import tempfile

import pytest

from prism.input.osm.exporter import TransitDataExporter
from prism.output.gtfs.gtfs_writer import GTFSWriter
from prism.misc.config import Configuration


@pytest.fixture(scope="module")
def osm_transit_data(request):
    root_dir = pathlib.Path(__file__).parents[0]
    filepath = root_dir.joinpath("data", "osm", "abidjan_test_data.osm.pbf")
    config = Configuration({})
    tde = TransitDataExporter(str(filepath), config.data)
    tde.extract()
    return tde


@pytest.fixture(scope="module")
def osm_transit_data_filtered_by_mode(request):
    root_dir = pathlib.Path(__file__).parents[0]
    filepath = root_dir.joinpath("data", "osm", "abidjan_test_data.osm.pbf")
    config = {"osm_filter": {"mode": ["bus"]}}
    checked_config = Configuration(config)
    tde = TransitDataExporter(str(filepath), checked_config.data)
    tde.extract()
    return tde


@pytest.fixture(scope="module")
def gtfs_writer(osm_transit_data):
    writer = GTFSWriter()

    writer.add_agencies(osm_transit_data.gtfs_agencies)
    writer.add_stops(osm_transit_data.gtfs_stops)
    writer.add_routes(osm_transit_data.gtfs_routes)
    writer.add_shapes(osm_transit_data.gtfs_shapes)
    schedule = osm_transit_data.gtfs_schedules
    writer.add_trips(schedule.trips)
    writer.add_stop_times(schedule.stop_times)
    writer.add_calendar(schedule.calendar)
    writer.add_frequencies(schedule.frequencies)
    return writer


@pytest.fixture(scope="module")
def gtfs_as_zipfile(gtfs_writer):
    filename = "{}.zip".format(tempfile.mktemp())
    print("Writing GTFS feed to %s" % filename)
    gtfs_writer.write_zipped(filename)
    return filename
