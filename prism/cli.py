#!env python

import os
import logging
from logging import FileHandler
from contextlib import contextmanager
from pathlib import Path

import argparse

from prism import __version__
from prism.output.csv.csv_writer import OSMTransportExtractorCSVWriter
from prism.output.gtfs.gtfs_writer import GTFSWriter
from prism.input.osm.exporter import TransitDataExporter
from prism.misc.config import Configuration


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, prospective_dir, option_string=None):
        if not os.path.isdir(prospective_dir):
            parser.print_usage()
            print('Try "{} --help" for help.\n'.format(parser.prog))
            parser.exit("Error: Invalid path: {0}".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            parser.print_usage()
            print('Try "{} --help" for help.\n'.format(parser.prog))
            parser.exit("Error: Unreadable dir: {0}".format(prospective_dir))


class readable_file(argparse.Action):
    def __call__(self, parser, namespace, prospective_file, option_string=None):
        if not os.path.isfile(prospective_file):
            parser.print_usage()
            print('Try "{} --help" for help.\n'.format(parser.prog))
            parser.exit("Error: Invalid file: {0}".format(prospective_file))
        if os.access(prospective_file, os.R_OK):
            setattr(namespace, self.dest, prospective_file)
        else:
            parser.print_usage()
            print('Try "{} --help" for help.\n'.format(parser.prog))
            parser.exit("Error: Unreadable file: {0}".format(prospective_file))


def cli():
    parser = argparse.ArgumentParser(
        prog="prism",
        epilog="Mobility open data, proudly crafted by the OpenStreetMap community - An open source tool by Jungle Bus",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Export GTFS feed from OpenStreetMap data",
    )
    parser.add_argument(
        "osm_file",
        metavar="osm_file",
        action=readable_file,
        nargs="?",
        default=argparse.SUPPRESS,
        help="an OSM data file in a format supported by osmium such as .osm.pbf",
    )
    parser.add_argument(
        "--output-gtfs",
        "-gtfs",
        action="store_true",
        help="output a GTFS feed from OSM data",
    )
    parser.add_argument(
        "--output-csv",
        "-csv",
        action="store_true",
        help="output a bunch of CSV files with OSM transport data",
    )

    parser.add_argument(
        "--config",
        "-c",
        metavar="FILE",
        type=argparse.FileType("r"),
        help="a configuration file",
    )
    parser.add_argument(
        "--outdir", action=readable_dir, default=".", help="output directory"
    )
    parser.add_argument(
        "--loglevel",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="the log level",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="show the version and exit",
    )

    args = parser.parse_args()
    if not hasattr(args, "osm_file"):
        parser.print_usage()
        parser.exit("Error: You need to specify an OSM file to use as input")

    if not args.output_gtfs and not args.output_csv:
        parser.exit(
            "Error: You need to specify at least one output type (-csv / -gtfs)"
        )

    if args.loglevel:
        logging.basicConfig(level=args.loglevel)
    logging.debug("OSM input file: %s", args.osm_file)
    logging.debug("Config input file: %s", args.config)
    logging.debug("Output directory: %s", args.outdir)
    logging.debug("Output GTFS ?: %s", args.output_gtfs)
    logging.debug("Output csv files ?: %s", args.output_csv)

    export_osm_data(
        args.osm_file, args.outdir, args.config, args.output_gtfs, args.output_csv
    )


def export_osm_data(osm_file, outdir, config, output_gtfs, output_csv):
    with capture_logs(outdir) as logfile:
        checked_config = Configuration(config)

        osm_transit_data = TransitDataExporter(osm_file, checked_config.data)
        osm_transit_data.extract()

        if output_gtfs:
            writer = GTFSWriter()

            schedules = osm_transit_data.gtfs_schedules
            writer.add_trips(schedules.trips)
            writer.add_stop_times(schedules.stop_times)
            writer.add_calendar(schedules.calendar)
            writer.add_frequencies(schedules.frequencies)
            writer.add_agencies(osm_transit_data.gtfs_agencies)
            writer.add_stops(osm_transit_data.gtfs_stops)
            writer.add_routes(osm_transit_data.gtfs_routes)
            writer.add_shapes(osm_transit_data.gtfs_shapes)
            if checked_config.data["use_osm_charge_as_fare"]:
                writer.add_fares(osm_transit_data.gtfs_fares)
            writer.add_feedinfo(checked_config.data["feed_info_to_use"])
            writer.add_attributions(
                {
                    "attribution_id": "42",
                    "organization_name": "Jungle Bus, © OpenStreetMap contributors",
                    "is_producer": "1",
                    "is_operator": "0",
                    "is_authority": "0",
                    "attribution_url": "https://www.openstreetmap.org/copyright",
                }
            )

            zip_file_path = os.path.join(
                outdir, checked_config.data["gtfs_output_name"]
            )

            writer.write_zipped(zip_file_path)
            logging.info("GTFS feed saved to {}".format(zip_file_path))

        if output_csv:
            csvwriter = OSMTransportExtractorCSVWriter()
            csvwriter.add_stop_points(osm_transit_data.csv_stop_points)
            csvwriter.add_lines(osm_transit_data.csv_lines)
            csvwriter.add_routes(osm_transit_data.csv_routes)
            csv_file_path = os.path.join(outdir, "as_csv.zip")
            csvwriter.write_zipped(csv_file_path)
            logging.info("CSV export saved to {}".format(csv_file_path))


@contextmanager
def capture_logs(outdir):
    logfile = os.path.join(outdir, "logs.txt")
    handler = FileHandler(logfile, mode="w")
    logging.getLogger().addHandler(handler)
    try:
        yield logfile
    finally:
        logging.getLogger().removeHandler(handler)


if __name__ == "__main__":
    cli()
