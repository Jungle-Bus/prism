def test_csv_lines_builder_without_config(osm_transit_data):
    lines, line_routes = osm_transit_data.csv_lines
    assert len(lines) == 7, "Wrong number of lines"
    first_line = [line for line in lines if line["line_id"] == "r10185142"][0]
    assert (
        first_line["name"] == "gbaka : Abobo Gare Mairie ↔ Kennedy Mosquée Ado"
    ), "Wrong line name"
    assert first_line["operator"] == "divers", "Wrong line operator"
    assert first_line["network"] == "Gbaka d'Abobo", "Wrong line network"
    assert first_line["mode"] == "bus", "Wrong line mode"
    assert first_line["charge"] == "150 FCFA", "Wrong line charge"
    assert (
        first_line["opening_hours"] == "Mo-Su,PH 05:00-22:00"
    ), "Wrong line opening_hours"
    assert first_line["frequency"] == "30", "Wrong line frequency"
    assert first_line["code"] is None, "Wrong line code"
    assert first_line["shape"] is not None

    routes_list = [
        elem["route_id"] for elem in line_routes if elem["line_id"] == "r10185142"
    ]
    assert len(routes_list) == 2, "Wrong number of route for this line"


def test_csv_routes_builder_without_config(osm_transit_data):
    routes, route_stop = osm_transit_data.csv_routes
    assert len(routes) == 14, "Wrong number of routes"
    one_route = [route for route in routes if route["route_id"] == "r10395135"][0]
    assert (
        one_route["name"] == "bateau-bus 503 : Yopougon (Abobo Doumé) → Plateau"
    ), "Wrong route name"
    assert one_route["operator"] == "SOTRA", "Wrong route operator"
    assert one_route["network"] == "monbato", "Wrong route network"
    assert one_route["mode"] == "ferry", "Wrong route mode"
    assert one_route["opening_hours"] is None, "Wrong route opening_hours"
    assert one_route["frequency"] is None, "Wrong route frequency"
    assert one_route["code"] == "503", "Wrong route code"
    assert one_route["shape"] is not None

    stops_list = [
        elem["stop_point_id"] for elem in route_stop if elem["route_id"] == "r10395135"
    ]
    assert len(stops_list) == 2, "Wrong number of stops for this route"


def test_csv_stops_builder_without_config(osm_transit_data):
    stops = [elem for elem in osm_transit_data.csv_stop_points]
    assert len(stops) == 111, "Wrong number of stops"
    one_stop = [stop for stop in stops if stop["stop_point_id"] == "n6903397404"][0]
    assert one_stop["name"] == "À l'École", "Wrong stop name"
    assert one_stop["shelter"] == "no", "Wrong stop shelter attribute"
    assert one_stop["wheelchair"] is None, "Wrong stop wheelchair attribute"


def test_csv_volumetries_with_config_filter_mode(osm_transit_data_filtered_by_mode):
    stops = [elem for elem in osm_transit_data_filtered_by_mode.csv_stop_points]
    assert len(stops) == 108, "Wrong number of stops"
    lines, line_route = osm_transit_data_filtered_by_mode.csv_lines
    assert len(lines) == 5, "Wrong number of lines"
    routes, route_stop = osm_transit_data_filtered_by_mode.csv_routes
    assert len(routes) == 10, "Wrong number of routes"
