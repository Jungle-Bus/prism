import io
import csv
import zipfile
from collections import OrderedDict

from prism.misc.models import GTFSFilesWithHeaders


class GTFSWriter(object):
    """GTFS feed writer."""

    def __init__(self):
        self._buffers = {}
        self._csv_writers = {}
        self._files = {}

        for name, csv_headers in self.headers.items():
            self._buffers[name] = io.StringIO()
            self._csv_writers[name] = csv.writer(
                self._buffers[name], lineterminator="\n"
            )
            self._csv_writers[name].writerow(csv_headers)

    def _add_records(self, name, records, sortkey=None):
        if sortkey:
            records = sorted(records, key=lambda x: x[sortkey])
        for rec in records:
            if not isinstance(rec, dict):
                record = rec._asdict()
            else:
                record = rec
            csv_record = OrderedDict.fromkeys(self.headers[name])
            # Update csv with keys present in headers. Skip anything else.
            csv_record.update(
                {k: v for k, v in record.items() if k in self.headers[name]}
            )
            self._csv_writers[name].writerow([v for v in csv_record.values()])

    @property
    def headers(self):
        """List of GTFS file names and their column headers.
        Only referenced headers will be exported."""
        return GTFSFilesWithHeaders

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

    def write_zipped(self, filepath):
        """Write the GTFS feed in the given file."""
        with zipfile.ZipFile(
            filepath, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zfile:
            for name, buffer in self._buffers.items():
                if len(buffer.getvalue().splitlines()) > 1:  # do not write empty files
                    encoded_values = io.BytesIO(buffer.getvalue().encode("utf-8"))
                    zfile.writestr("{}.txt".format(name), encoded_values.getbuffer())
            for name, path in self._files.items():
                zfile.write(path, arcname=name)
