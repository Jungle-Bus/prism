import logging
import osmium as o

from prism.misc.models import OSMRoute, OSMLine


class RelationHandler(o.SimpleHandler):
    def __init__(self, config):
        super(RelationHandler, self).__init__()
        self.lines = []
        self.routes = {}
        self.all_related_nodes = []
        self.all_related_ways = []

        self.config_only_modes = None
        self.config_only_networks = None
        self.config_only_operators = None

        if "osm_filter" in config:
            if "mode" in config["osm_filter"] and config["osm_filter"]["mode"]:
                self.config_only_modes = config["osm_filter"]["mode"]
                logging.debug(
                    "Only keeping these OSM modes : {}".format(self.config_only_modes)
                )
            if "network" in config["osm_filter"] and config["osm_filter"]["network"]:
                self.config_only_networks = config["osm_filter"]["network"]
                logging.debug(
                    "Only keeping these OSM networks : {}".format(
                        self.config_only_networks
                    )
                )
            if "operator" in config["osm_filter"] and config["osm_filter"]["operator"]:
                self.config_only_operators = config["osm_filter"]["operator"]
                logging.debug(
                    "Only keeping these OSM operators : {}".format(
                        self.config_only_operators
                    )
                )

        self.non_osm_pt_modes = [
            "bicycle",
            "canoe",
            "detour",
            "fitness_trail",
            "foot",
            "hiking",
            "horse",
            "inline_skates",
            "mtb",
            "nordic_walking",
            "pipeline",
            "piste",
            "power",
            "proposed",
            "road",
            "railway",  # only infrastructure, not for passenger info
            "running",
            "ski",
            "historic",
            "path",
            "junction",
            "tracks",
        ]

    def relation(self, rel):
        rel_type = rel.tags.get("type")
        rel_mode = rel.tags.get("route_master") or rel.tags.get("route")
        if any(
            [
                rel.deleted,
                not rel.visible,
                rel_mode in self.non_osm_pt_modes,
                rel_type not in ["route", "route_master"],
            ]
        ):
            return

        if self.config_only_modes:
            if rel_mode not in self.config_only_modes:
                return

        if self.config_only_networks:
            if rel.tags.get("network") not in self.config_only_networks:
                return

        if self.config_only_operators:
            if rel.tags.get("operator") not in self.config_only_operators:
                return

        relation_id = "r{}".format(rel.id)
        if rel_type == "route_master":
            routes_list = []
            for rm in rel.members:
                if rm.type == "r":
                    routes_list.append("r{}".format(rm.ref))
            line = OSMLine(relation_id, {t.k: t.v for t in rel.tags}, routes_list)
            self.lines.append(line)

        if rel_type == "route":
            stops_list = []
            ways_list = []
            for rm in rel.members:
                if rm.type == "n" and rm.role in [
                    "platform",
                    "platform_entry_only",
                    "platform_exit_only",
                ]:
                    stops_list.append("n{}".format(rm.ref))
                    self.all_related_nodes.append(rm.ref)
                if rm.type == "w" and rm.role == "":
                    ways_list.append(rm.ref)
                    self.all_related_ways.append(rm.ref)
            self.routes[relation_id] = OSMRoute(
                relation_id, {t.k: t.v for t in rel.tags}, stops_list, ways_list
            )
