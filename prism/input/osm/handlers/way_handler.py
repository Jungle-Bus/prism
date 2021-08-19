import logging
import osmium as o

from prism.misc.models import OSMWay, LatLon


class WayHandler(o.SimpleHandler):
    def __init__(self, requested_ways):
        super(WayHandler, self).__init__()
        self.requested_ways = requested_ways
        self.ways = {}

    def way(self, w):
        if w.id not in self.requested_ways:
            return

        points_in_way = []
        for n in w.nodes:
            try:
                points_in_way.append(LatLon(n.location.lat, n.location.lon))
            except o.InvalidLocationError:
                logging.debug("InvalidLocationError at way %s node %s", w.id, n.ref)

        self.ways[w.id] = OSMWay(w.id, points_in_way)
