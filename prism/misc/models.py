from collections import namedtuple

# OSM
OSMLine = namedtuple("OSMLine", ["id", "tags", "routes_list"])
OSMRoute = namedtuple("OSMRoute", ["id", "tags", "stops_list", "ways_list"])

OSMStop = namedtuple("OSMStop", ["id", "lon", "lat", "tags"])

OSMWay = namedtuple("OSMWay", ["id", "points_list"])
LatLon = namedtuple("LatLon", ["lat", "lon"])

# GTFS
Agency = namedtuple(
    "Agency",
    ["agency_id", "agency_url", "agency_name", "agency_timezone", "agency_lang"],
)

Route = namedtuple(
    "Route",
    [
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_type",
        "route_url",
        "route_color",
        "route_text_color",
        "agency_id",
    ],
)

Stop = namedtuple(
    "Stop",
    [
        "stop_id",
        "stop_name",
        "stop_lon",
        "stop_lat",
        "stop_code",
        "wheelchair_boarding",
        "location_type",
        "parent_station",
    ],
)

ShapePoint = namedtuple(
    "ShapePoint", ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
)

FareAttributes = namedtuple(
    "FareAttributes",
    ["fare_id", "price", "currency_type", "payment_method", "transfers", "agency_id"],
)

FareRule = namedtuple("FareRule", ["fare_id", "route_id"])

GTFSSchedule = namedtuple(
    "GTFSSchedule", ["calendar", "stop_times", "trips", "frequencies"]
)

GTFSFilesWithHeaders = {
    "agency": [
        "agency_id",
        "agency_name",
        "agency_url",
        "agency_timezone",
        "agency_lang",
        "agency_phone",
        "agency_fare_url",
        "agency_email",
    ],
    "stops": [
        "stop_id",
        "stop_code",
        "stop_name",
        "stop_desc",
        "stop_lat",
        "stop_lon",
        "zone_id",
        "stop_url",
        "location_type",
        "parent_station",
        "stop_timezone",
        "wheelchair_boarding",
    ],
    "routes": [
        "route_id",
        "agency_id",
        "route_short_name",
        "route_long_name",
        "route_desc",
        "route_type",
        "route_url",
        "route_color",
        "route_text_color",
    ],
    "trips": [
        "route_id",
        "service_id",
        "trip_id",
        "trip_headsign",
        "direction_id",
        "shape_id",
    ],
    "calendar": [
        "service_id",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "start_date",
        "end_date",
    ],
    "stop_times": [
        "trip_id",
        "arrival_time",
        "departure_time",
        "stop_id",
        "timepoint",
        "stop_sequence",
    ],
    "shapes": ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"],
    "frequencies": ["trip_id", "start_time", "end_time", "headway_secs"],
    "fare_attributes": [
        "fare_id",
        "price",
        "currency_type",
        "payment_method",
        "transfers",
        "agency_id",
    ],
    "fare_rules": ["fare_id", "route_id"],
    "attributions": [
        "attribution_id",
        "agency_id",
        "route_id",
        "trip_id",
        "organization_name",
        "is_producer",
        "is_operator",
        "is_authority",
        "attribution_url",
    ],
    "feed_info": [
        "feed_publisher_name",
        "feed_publisher_url",
        "feed_lang",
        "feed_start_date",
        "feed_end_date",
        "feed_version",
        "default_lang",
        "feed_contact_email",
        "feed_contact_url",
    ],
}

# OSMTransportExtractor CSV
CSVFilesWithHeaders = {
    "stop_points": [
        "stop_point_id",
        "name",
        "latitude",
        "longitude",
        "local_ref",
        "wheelchair",
        "shelter",
    ],
    "lines": [
        "line_id",
        "name",
        "code",
        "colour",
        "operator",
        "network",
        "mode",
        "frequency",
        "opening_hours",
        "frequency_exceptions",
        "charge",
        "wheelchair",
        "shape",
    ],
    "line_routes": ["line_id", "route_id"],
    "route_stops": ["route_id", "stop_point_id"],
    "routes": [
        "route_id",
        "name",
        "code",
        "destination",
        "origin",
        "colour",
        "operator",
        "network",
        "mode",
        "frequency",
        "opening_hours",
        "frequency_exceptions",
        "travel_time",
        "shape",
    ],
}
