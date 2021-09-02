from prism.misc.models import CSVFilesWithHeaders
from prism.output.csv_writer import GenericCSVWriter


class OSMTransportExtractorCSVWriter(GenericCSVWriter):
    @property
    def headers(self):
        return CSVFilesWithHeaders

    def add_stop_points(self, stop_points):
        self._add_records("stop_points", stop_points)

    def add_lines(self, lines):
        self._add_records("lines", lines[0])
        self._add_records("line_routes", lines[1])

    def add_routes(self, routes):
        self._add_records("routes", routes[0])
        self._add_records("route_stops", routes[1])
