def test_gtfs_stops_builder_without_config(osm_transit_data):
    stops = [elem for elem in osm_transit_data.gtfs_stops]
    assert len(stops) == 111, "Wrong number of stops"
    first_stop = stops[0]
    assert first_stop.stop_id == "n6195348341", "Wrong stop_id"
    assert first_stop.stop_name == "CCIA", "Wrong stop_name"
    assert first_stop.stop_lon == -4.021322, "Wrong stop_lon"
    assert first_stop.stop_lat == 5.3317403, "Wrong stop_lat"
    assert first_stop.stop_code == "", "Wrong stop_code"
    assert first_stop.wheelchair_boarding == 0, "Wrong stop wheelchair_boarding"
    assert first_stop.location_type == 0, "Wrong stop location_type"
    assert first_stop.parent_station == "", "Wrong stop parent_station"


def test_gtfs_agencies_builder_without_config(osm_transit_data):
    agencies = [elem for elem in osm_transit_data.gtfs_agencies]
    assert len(agencies) == 2, "Wrong number of agencies"
    first_agency = agencies[0]
    assert first_agency.agency_id == "divers", "Wrong agency_id"
    assert first_agency.agency_timezone == "Europe/Paris", "Wrong agency_timezone"
    assert first_agency.agency_lang == "fr", "Wrong agency_lang"


def test_gtfs_routes_builder_without_config(osm_transit_data):
    routes = [elem for elem in osm_transit_data.gtfs_routes]
    assert len(routes) == 7, "Wrong number of routes"
    first_gtfs_route = routes[0]
    assert first_gtfs_route.route_id == "r10185142", "Wrong route_id"
    assert first_gtfs_route.route_short_name == "", "Wrong route_short_name"
    assert (
        first_gtfs_route.route_long_name
        == "gbaka : Abobo Gare Mairie ↔ Kennedy Mosquée Ado"
    ), "Wrong route_long_name"
    assert first_gtfs_route.route_type == 3, "Wrong route_type"
    assert first_gtfs_route.route_color == "", "Wrong route_color"


def test_gtfs_schedule_builder_without_config(osm_transit_data):
    schedules = osm_transit_data.gtfs_schedules
    first_frequency = schedules.frequencies[0]
    assert first_frequency["start_time"] == "05:00:00", "Wrong start_time"
    assert first_frequency["end_time"] == "22:00:00", "Wrong end_time"
    assert first_frequency["headway_secs"] == 1800, "Wrong headway_secs"
    random_trip_id = first_frequency["trip_id"]
    random_trip = [
        elem for elem in schedules.trips if elem["trip_id"] == random_trip_id
    ][0]
    assert random_trip["route_id"] == "r10185142", "Wrong route_id in trips"
    assert random_trip["shape_id"] == "r10185123", "Wrong shape_id in trips"
    assert random_trip["service_id"] == "Mo-Su", "Wrong service_id in trips"
    assert random_trip["trip_headsign"] == "Mosquée Ado", "Wrong trip_headsign"
    assert random_trip["trip_id"] == "r10185123_Mo-Su", "Wrong trip_id"


def test_gtfs_shapes_builder_without_config(osm_transit_data):
    shapes = [elem for elem in osm_transit_data.gtfs_shapes]
    gtfs_shapes = shapes[0]
    assert len(shapes) == 2137, "Wrong number of shapes"
    assert gtfs_shapes.shape_id == "r10185122", "Wrong shape_id"
    assert gtfs_shapes.shape_pt_lat == 5.4236201, "Wrong shape_pt_lat"
    assert gtfs_shapes.shape_pt_lon == -3.9978131, "Wrong shape_pt_lon"
    assert gtfs_shapes.shape_pt_sequence == 0, "Wrong shape_pt_sequence"


def test_agencies_referenced_in_routes_actually_exist(osm_transit_data):
    agencies_ids = set(agency.agency_id for agency in osm_transit_data.gtfs_agencies)
    for route in osm_transit_data.gtfs_routes:
        assert (
            route.agency_id in agencies_ids
        ), "At least one agency referenced in routes that does not exist"


def test_all_objects_referenced_in_trips_actually_exist(osm_transit_data):
    routes_id = set(route.route_id for route in osm_transit_data.gtfs_routes)
    services_id = set(
        service["service_id"] for service in osm_transit_data.gtfs_schedules.calendar
    )
    shape_ids = set(shape.shape_id for shape in osm_transit_data.gtfs_shapes)
    shape_ids.add("")  # shapes are optionnal, it's ok too if we don't have one
    for trip in osm_transit_data.gtfs_schedules.trips:
        assert (
            trip["route_id"] in routes_id
        ), "At least one route referenced in trips that does not exist"
        assert (
            trip["service_id"] in services_id
        ), "At least one calendar referenced in trips that does not exist"
        assert (
            trip["shape_id"] in shape_ids
        ), "At least one shape referenced in trips that does not exist"


def test_all_objects_referenced_in_stop_times_actually_exist(osm_transit_data):
    trips_id = set(trip["trip_id"] for trip in osm_transit_data.gtfs_schedules.trips)
    stops_ids = set(stop.stop_id for stop in osm_transit_data.gtfs_stops)
    for stop_time in osm_transit_data.gtfs_schedules.stop_times:
        assert (
            stop_time["trip_id"] in trips_id
        ), "At least one trip referenced in stop_times that does not exist"
        assert (
            stop_time["stop_id"] in stops_ids
        ), "At least one stop referenced in stop_times that does not exist"


def test_volumetries_with_config_filter_mode(osm_transit_data_filtered_by_mode):
    stops = [elem for elem in osm_transit_data_filtered_by_mode.gtfs_stops]
    assert len(stops) == 108, "Wrong number of stops"
    agencies = [elem for elem in osm_transit_data_filtered_by_mode.gtfs_agencies]
    assert len(agencies) == 2, "Wrong number of agencies"
    routes = [elem for elem in osm_transit_data_filtered_by_mode.gtfs_routes]
    assert len(routes) == 5, "Wrong number of routes"
