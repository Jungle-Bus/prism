from prism.misc.models import GTFSFilesWithHeaders
from prism.output.csv_writer import GenericCSVWriter


class GTFSWriter(GenericCSVWriter):
    """GTFS feed writer."""

    @property
    def headers(self):
        """List of GTFS file names and their column headers.
        Only referenced headers will be exported."""
        return GTFSFilesWithHeaders

    @property
    def file_extention(self):
        return "txt"

    def add_agencies(self, agencies):
        self._add_records("agency", agencies)

    def add_stops(self, stops):
        self._add_records("stops", stops)

    def add_routes(self, routes):
        self._add_records("routes", routes, sortkey=0)

    def add_calendar(self, weekly_schedules):
        self._add_records("calendar", weekly_schedules)

    def add_trips(self, trips):
        self._add_records("trips", trips)

    def add_stop_times(self, stop_times):
        self._add_records("stop_times", stop_times)

    def add_shapes(self, shapes):
        self._add_records("shapes", shapes)

    def add_fares(self, fares):
        self._add_records("fare_attributes", fares[0])
        self._add_records("fare_rules", fares[1])

    def add_frequencies(self, frequencies):
        self._add_records("frequencies", frequencies)

    def add_feedinfo(self, info):
        self._add_records("feed_info", [info])

    def add_attributions(self, info):
        self._add_records("attributions", [info])
