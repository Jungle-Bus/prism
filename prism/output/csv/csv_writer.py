import io
import csv
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

    def add_additional_tags(self, add_tags, add_tags_config):
        headers = ["object", "id"] + list(
            set([item for sublist in add_tags_config.values() for item in sublist])
        )
        self._buffers["additional_tags"] = io.StringIO()
        self._csv_writers["additional_tags"] = csv.DictWriter(
            self._buffers["additional_tags"], lineterminator="\n", fieldnames=headers
        )

        self._csv_writers["additional_tags"].writeheader()
        for elem in add_tags:
            self._csv_writers["additional_tags"].writerow(elem)
