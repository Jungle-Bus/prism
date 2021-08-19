import logging

import osmium as o

from prism.misc.models import OSMStop


class NodeHandler(o.SimpleHandler):
    def __init__(self, requested_nodes):
        super(NodeHandler, self).__init__()
        self.requested_nodes = requested_nodes
        self.stops = {}

    def node(self, n):
        if n.id not in self.requested_nodes:
            return

        stop_id = "n{}".format(n.id)
        self.stops[stop_id] = OSMStop(
            stop_id, n.location.lon, n.location.lat, {t.k: t.v for t in n.tags}
        )
