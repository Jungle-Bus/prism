import io
import csv
import zipfile
from collections import OrderedDict


class GenericCSVWriter(object):
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
        """List of csv file names and their column headers.
        Only referenced headers will be exported."""
        return {"file1": ["column1", "column2"]}

    @property
    def file_extention(self):
        return "csv"

    def write_zipped(self, filepath):
        with zipfile.ZipFile(
            filepath, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zfile:
            for name, buffer in self._buffers.items():
                if len(buffer.getvalue().splitlines()) > 1:  # do not write empty files
                    encoded_values = io.BytesIO(buffer.getvalue().encode("utf-8"))
                    zfile.writestr(
                        "{}.{}".format(name, self.file_extention),
                        encoded_values.getbuffer(),
                    )
            for name, path in self._files.items():
                zfile.write(path, arcname=name)
