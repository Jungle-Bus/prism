import logging
import os
import json
import csv

from datetime import timedelta, datetime

from prism.misc.models import Agency


class Configuration(object):
    def __init__(self, config_args):
        """Contructor function
        Based on the configuration from the config file
        it prepares all mandatory configuration elements.
        """
        self.from_user = self.load_config(config_args)
        self.data = {}

        self.prepare_use_network_as_agency()
        self.prepare_default_stop_name()
        self.prepare_default_agency()
        self.prepare_osm_filters()
        self.prepare_use_charge_as_fare()
        self.prepare_algo_to_compute_GTFS_stop_times()
        self.prepare_algo_to_enumerate_GTFS_trips()
        self.prepare_feed_info()
        self.prepare_dates()
        self.prepare_gtfs_output_file_name()
        self.prepare_csv_additional_tag_exports()

    def load_config(self, config_args):
        if config_args is None:
            return {}

        if type(config_args).__name__ == "dict":
            return config_args

        if type(config_args).__name__ == "str":
            if os.path.isfile(config_args):
                with open(config_args) as json_file:
                    config = Configuration.load_config_file(json_file)
            else:
                logging.error("No config.json file found")

        else:
            config = Configuration.load_config_file(config_args)

        return config

    @staticmethod
    def load_config_file(configfile):
        """
        Loads json from config file
        """
        try:
            config = json.load(configfile)
        except ValueError as e:
            logging.error("Config json file is not valid")
            logging.error(e)

        return config

    def prepare_default_agency(self):
        """
        Specifies default values for GTFS agencies
        """

        default_agency_values = self.from_user.get("default_agency") or {}

        self.data["default_agency_to_use"] = Agency(
            default_agency_values.get("agency_id") or -1,
            default_agency_values.get("agency_url") or "https://gtfs.org",
            default_agency_values.get("agency_name") or "Unknown agency",
            default_agency_values.get("agency_timezone") or "Europe/Paris",
            default_agency_values.get("agency_lang") or "fr",
        )

    def prepare_default_stop_name(self):
        """
        Specifies the GTFS stop_name to use when OSM tag is not set on stops
        """

        if not "default_stop_name" in self.from_user:
            self.data["default_stop_name"] = "[Stop]"
            return

        self.data["default_stop_name"] = self.from_user["default_stop_name"]

    def prepare_osm_filters(self):
        """
        Specifies which OSM lines and routes should be extracted
        It keeps only the specified ones & filters are cumulatives
        """
        acceptable_filters = ["mode", "operator", "network"]
        at_least_one_ok_filter = False
        if self.from_user.get("osm_filter"):
            for filter_type in self.from_user["osm_filter"].keys():
                if filter_type in acceptable_filters:
                    at_least_one_ok_filter = True
                    if type(self.from_user["osm_filter"][filter_type]) != list:
                        logging.error(
                            "Invalid values in config file for OSM {} filters, will be ignored".format(
                                filter_type
                            )
                        )
                        continue
                    if not "osm_filter" in self.data:
                        self.data["osm_filter"] = {}
                    self.data["osm_filter"][filter_type] = self.from_user["osm_filter"][
                        filter_type
                    ]
            if not at_least_one_ok_filter:
                logging.error(
                    "No valid OSM filters found in config file, will keep all lines"
                )

    def prepare_use_network_as_agency(self):
        """
        Specifies if OSM network tag should be used to create GTFS Agencies
        instead of operator one
        """

        if self.from_user.get("use_network_as_agency") in ["True", "yes", "1"]:
            self.data["use_network_as_agency"] = True
            return

        self.data["use_network_as_agency"] = False

    def prepare_use_charge_as_fare(self):
        """
        Specifies if OSM charge tag on OSM route_master should be used to create
        GTFS Fares (with no transfers)
        """

        if self.from_user.get("use_osm_charge_as_fare") in ["True", "yes", "1"]:
            self.data["use_osm_charge_as_fare"] = True
            return

        self.data["use_osm_charge_as_fare"] = False

    def prepare_feed_info(self):
        """
        Set GTFS feed info
        """
        feed_info_values = self.from_user.get("feed_info") or {}
        now = datetime.now()

        self.data["feed_info_to_use"] = {
            "feed_publisher_name": feed_info_values.get("feed_publisher_name")
            or "Jungle Bus",
            "feed_publisher_url": feed_info_values.get("feed_publisher_url")
            or "https://junglebus.io",
            "feed_version": feed_info_values.get("feed_version")
            or now.strftime("%Y%m%d%H%M"),
            "feed_lang": feed_info_values.get("feed_lang") or "fr",
            "default_lang": feed_info_values.get("default_lang") or "",
            "feed_contact_email": feed_info_values.get("feed_contact_email")
            or "contact@junglebus.io",
            "feed_contact_url": feed_info_values.get("feed_contact_url") or "",
        }

    def prepare_gtfs_output_file_name(self):
        """
        Specifies the name of the output GTFS zip file
        """

        if not "gtfs_output_name" in self.from_user:
            self.data["gtfs_output_name"] = "output_gtfs.zip"
            return

        self.data["gtfs_output_name"] = self.from_user["gtfs_output_name"]

    def prepare_algo_to_compute_GTFS_stop_times(self):
        """
        Specifies how to compute duration between each stop of each route of a GTFS
        With speed_by_mode algo (default and fallback): use the distance between stops and a constant speed value for each osm mode
        With osm_duration_tag algo: use the total trip duration from OSM to compute speed, then use distance between stops
        """
        default = {
            "algo": "speed_by_mode",
            "speed_by_mode": {
                "bus": 20,
                "ferry": 15,
                "train": 70,
                "tram": 25,
                "subway": 30,
            },
        }

        how_to = self.from_user.get("make_stop_times")
        if not how_to:
            self.data["make_stop_times"] = default
            return

        algo = self.from_user["make_stop_times"].get("algo")
        if algo not in ["speed_by_mode", "osm_duration_tag"]:
            logging.error(
                "No valid algo to make stop times found in config file, will use constant speed values"
            )
            self.data["make_stop_times"] = default
            return

        self.data["make_stop_times"] = {"algo": algo}

        speed_by_mode = self.from_user["make_stop_times"].get("speed_by_mode")
        if not speed_by_mode:
            self.data["make_stop_times"][speed_by_mode] = default["speed_by_mode"]
            return

        self.data["make_stop_times"]["speed_by_mode"] = speed_by_mode
        for mode, speed in speed_by_mode.items():
            if mode not in default["speed_by_mode"]:
                logging.debug("Unknown mode {} in config file".format(mode))
                continue
            default_speed = default["speed_by_mode"][mode]
            try:
                i_speed = int(speed)
                self.data["make_stop_times"]["speed_by_mode"][mode] = i_speed
                if not i_speed < 130:
                    logging.debug(
                        "Speed for {} mode in config file seems too high. Is it in km/h ?".format(
                            mode
                        )
                    )
            except ValueError as e:
                self.data["make_stop_times"]["speed_by_mode"][mode] = default_speed
                logging.debug(
                    "Invalid speed value ({} km/h) for {} mode in config file. Will use default value ({} km/h)".format(
                        speed, mode, default_speed
                    )
                )

        for mode, speed in default["speed_by_mode"].items():
            if mode not in self.data["make_stop_times"]["speed_by_mode"]:
                self.data["make_stop_times"]["speed_by_mode"][mode] = speed

    def prepare_algo_to_enumerate_GTFS_trips(self):
        """
        Specifies how to enumerate the trips for each route of a GTFS
        With osm_interval_tag algo (default and fallback): use the interval, opening_hours, and interval:conditional tags
            on OSM route_master or route objets. It will create one trip for each day period and add frequencies.
        With departures_at_first_stop_as_csv algo: use an external file with time of departure at the first stop of each
            GTFS trip. It will create as much trips. External file path goes in external_schedule_file attribute,
            it should be a csv file with the following columns:
                - route_id (matching OSM route osm_id)
                - departure_time (for instance 07:40:00)
                - first_stop_index (index of the first stop to use in trip, starting at 1. Optional, will start at first stop if not provided)
                - last_stop_index (index of the last stop to use in trip, starting at 1. Optional, will use all the stops if not provided)
        """
        default = {
            "algo": "osm_interval_tag",
            "use_default_interval_if_empty": True,
            "departures_by_route_id": {},
        }
        self.data["enumerate_trips"] = default

        how_to = self.from_user.get("enumerate_trips")
        if not how_to:
            self.data["enumerate_trips"] = default
            return

        algo = self.from_user["enumerate_trips"].get("algo")
        if algo not in ["osm_interval_tag", "departures_at_first_stop_as_csv"]:
            logging.error(
                "No valid algo to enumerate trips found in config file, will use interval and opening_hours tags in OSM"
            )
            self.data["enumerate_trips"] = default
            return

        self.data["enumerate_trips"]["algo"] = algo

        if self.from_user["enumerate_trips"].get("use_default_interval_if_empty") in [
            "False",
            "no",
            "0",
        ]:
            self.data["enumerate_trips"]["use_default_interval_if_empty"] = False
        else:
            self.data["enumerate_trips"]["use_default_interval_if_empty"] = True

        if self.data["enumerate_trips"]["algo"] == "departures_at_first_stop_as_csv":
            external_file_path = self.from_user["enumerate_trips"].get(
                "external_schedule_file"
            )
            if not external_file_path:
                logging.error(
                    "No external file path for departures found in config file, will use interval and opening_hours tags in OSM instead"
                )
                self.data["enumerate_trips"] = default
                return
            if not os.path.isfile(external_file_path):
                logging.error(
                    "Unable to find external file path for departures found using config file, will use interval and opening_hours tags in OSM instead"
                )
                self.data["enumerate_trips"] = default
                return

            departures_by_route_id = {}
            try:
                with open(external_file_path, "r") as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=",")
                    for row in csv_reader:
                        if row["route_id"] not in departures_by_route_id:
                            departures_by_route_id[row["route_id"]] = []
                        if not "first_stop_index" in row:
                            row["first_stop_index"] = None
                        if not "last_stop_index" in row:
                            row["last_stop_index"] = None
                        departures_by_route_id[row["route_id"]].append(
                            {
                                "departure": datetime.strptime(
                                    row["departure_time"], "%H:%M:%S"
                                ),
                                "first_stop_index": row["first_stop_index"] or None,
                                "last_stop_index": row["last_stop_index"] or None,
                            }
                        )
                self.data["enumerate_trips"][
                    "departures_by_route_id"
                ] = departures_by_route_id
            except Exception as e:
                logging.error(
                    "Unable to process external file path for departures found using config file: {}. Will use interval and opening_hours tags in OSM instead"
                )

    def prepare_dates(self):
        """
        Validate and prepare start and end date.
        Either from config file or based on current date.
        """
        feed_info_values = self.from_user.get("feed_info") or {}
        validated_start_date = None
        validated_end_date = None

        if "feed_start_date" in feed_info_values:
            try:
                validated_start_date = datetime.strptime(
                    feed_info_values["feed_start_date"], "%Y%m%d"
                )
                start_date = feed_info_values["feed_start_date"]
            except ValueError:
                logging.error(
                    "Invalid feed_start_date {}, will use generated one".format(
                        feed_info_values["feed_start_date"]
                    )
                )

        if not validated_start_date:
            # Use beginning of current month
            now = datetime.now()
            start_date = now.strftime("%Y%m") + "01"
            validated_start_date = datetime.strptime(start_date, "%Y%m%d")

        if "feed_end_date" in feed_info_values:
            try:
                validated_end_date = datetime.strptime(
                    feed_info_values["feed_end_date"], "%Y%m%d"
                )
                end_date = feed_info_values["feed_end_date"]
            except ValueError:
                logging.error(
                    "Invalid feed_end_date {}, will use generated one".format(
                        feed_info_values["feed_end_date"]
                    )
                )

        if not validated_end_date:
            validated_end_date = validated_start_date + timedelta(days=180)
            end_date = validated_end_date.strftime("%Y%m%d")

        logging.debug("GTFS feed start date: {}".format(start_date))
        logging.debug("GTFS feed end date: {}".format(end_date))

        self.data["feed_info_to_use"]["feed_start_date"] = start_date
        self.data["feed_info_to_use"]["feed_end_date"] = end_date

    def prepare_csv_additional_tag_exports(self):
        """
        Export some more tags from OSM (in the csv export only)
        """

        if not "additional_tags_export" in self.from_user:
            self.data["additional_tags_export"] = None
            return

        acceptable_tags_categories = ["stop_point", "route", "line"]
        at_least_one_ok_category = False
        if self.from_user.get("additional_tags_export"):
            for filter_type in self.from_user["additional_tags_export"].keys():
                print()
                if filter_type in acceptable_tags_categories:
                    at_least_one_ok_category = True
                    if (
                        type(self.from_user["additional_tags_export"][filter_type])
                        != list
                    ):
                        logging.error(
                            "Invalid values in config file for OSM additional tags export for {}, will be ignored".format(
                                filter_type
                            )
                        )
                        continue
                    if not "additional_tags_export" in self.data:
                        self.data["additional_tags_export"] = {}
                    self.data["additional_tags_export"][filter_type] = self.from_user[
                        "additional_tags_export"
                    ][filter_type]
                else:
                    logging.error(
                        "Invalid tag category {} in config file for OSM additional tags export, will be ignored. Valid categories are stop_point, line and route.".format(
                            filter_type
                        )
                    )
            if not at_least_one_ok_category:
                logging.error(
                    "No valid OSM additional tags export found in config file, no additional tag will be exported"
                )
