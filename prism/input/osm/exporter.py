import logging

from prism.input.osm.handlers import RelationHandler, NodeHandler, WayHandler
from prism.input.osm.handlers import get_geom_for_routes
from prism.output.gtfs.builders import (
    build_routes,
    build_stops,
    build_agencies,
    build_shapes,
    build_fares,
    build_schedules,
)
from prism.output.csv.builders import (
    build_csv_stop_points_export,
    build_csv_lines_export,
    build_csv_routes_export,
)


class TransitDataExporter(object):
    def __init__(self, osm_filename, config):
        self.osm_filename = osm_filename
        self.config = config
        self.relations = None
        self.nodes = None
        self.ways = None
        self.geom = None

    @property
    def gtfs_agencies(self):
        return build_agencies(self.relations.lines, self.config)

    @property
    def gtfs_routes(self):
        return build_routes(self.relations.lines, self.relations.routes, self.config)

    @property
    def gtfs_stops(self):
        return build_stops(self.nodes.stops, self.config)

    @property
    def gtfs_shapes(self):
        return build_shapes(self.geom)

    @property
    def gtfs_fares(self):
        return build_fares(self.relations.lines, self.config)

    @property
    def gtfs_schedules(self):
        return build_schedules(
            self.relations.lines,
            self.relations.routes,
            self.nodes.stops,
            self.geom,
            self.config,
        )

    @property
    def csv_stop_points(self):
        return build_csv_stop_points_export(self.nodes.stops, self.config)

    @property
    def csv_lines(self):
        return build_csv_lines_export(self.relations.lines, self.geom, self.config)

    @property
    def csv_routes(self):
        return build_csv_routes_export(self.relations.routes, self.geom, self.config)

    def extract(self):
        # Extract relations
        self.relations = RelationHandler(self.config)
        self.relations.apply_file(self.osm_filename)

        logging.debug("Found %d public transport lines", len(self.relations.lines))
        logging.debug("Found %d public transport routes", len(self.relations.routes))

        # Extract nodes
        self.nodes = NodeHandler(self.relations.all_related_nodes)
        self.nodes.apply_file(self.osm_filename, locations=True)

        logging.debug("Found %d stops", len(self.nodes.stops))

        # Extract ways
        self.ways = WayHandler(self.relations.all_related_ways)
        self.ways.apply_file(self.osm_filename, locations=True)

        logging.debug("Found %d ways", len(self.ways.ways))

        # Transform ways to route geom
        self.geom = get_geom_for_routes(
            self.relations.routes, self.ways.ways, self.nodes.stops
        )

        logging.debug("Built %d geom for public transport routes", len(self.geom))
