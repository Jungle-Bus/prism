from prism.misc.config import Configuration


def test_no_config(request):
    config_checked = Configuration({})
    config = config_checked.data

    assert not config["use_network_as_agency"]
    assert not config["use_osm_charge_as_fare"]
    assert config["default_stop_name"] == "[Stop]"
    assert config["default_agency_to_use"].agency_name == "Unknown agency"
    assert config["default_agency_to_use"].agency_timezone == "Europe/Paris"

    assert config["make_stop_times"]["algo"] == "speed_by_mode"
    assert config["make_stop_times"]["speed_by_mode"]["bus"] == 20

    assert config["enumerate_trips"]["algo"] == "osm_interval_tag"
    assert config["enumerate_trips"]["use_default_interval_if_empty"]
    assert config["enumerate_trips"]["departures_by_route_id"] == {}

    assert "feed_start_date" in config["feed_info_to_use"]

    assert config["gtfs_output_name"] == "output_gtfs.zip"

    assert not config["additional_tags_export"]


def test_sample_config(request):
    from_user = {
        "default_agency": {
            "agency_id": "divers",
            "agency_timezone": "Africa/Abidjan",
            "agency_lang": "fr",
            "agency_phone": "",
            "agency_fare_url": "",
        },
        "feed_info": {"feed_start_date": "20200101", "feed_end_date": "20201231"},
        "make_stop_times": {
            "algo": "osm_duration_tag",
            "speed_by_mode": {"ferry": "25", "bateau-bus": "25"},
        },
        "enumerate_trips": {
            "algo": "osm_interval_tag",
            "use_default_interval_if_empty": "False",
        },
        "default_stop_name": "[Unamed stop]",
        "use_osm_charge_as_fare": "True",
        "use_network_as_agency": "True",
        "gtfs_output_name": "GTFS_Abidjan.zip",
        "osm_filter": {"mode": ["bus", "ferry"], "operator": ["Citrans"]},
        "additional_tags_export": {
            "stop_point": ["shelter"],
            "route": ["public_transport:version"],
        },
    }
    config_checked = Configuration(from_user)
    config = config_checked.data

    assert config["use_network_as_agency"]
    assert config["use_osm_charge_as_fare"]
    assert config["default_stop_name"] == "[Unamed stop]"
    assert config["default_agency_to_use"].agency_name == "Unknown agency"
    assert config["default_agency_to_use"].agency_timezone == "Africa/Abidjan"

    assert config["make_stop_times"]["algo"] == "osm_duration_tag"
    assert config["make_stop_times"]["speed_by_mode"]["bus"] == 20
    assert config["make_stop_times"]["speed_by_mode"]["ferry"] == 25

    assert config["enumerate_trips"]["algo"] == "osm_interval_tag"
    assert not config["enumerate_trips"]["use_default_interval_if_empty"]
    assert config["enumerate_trips"]["departures_by_route_id"] == {}

    assert config["feed_info_to_use"]["feed_start_date"] == "20200101"

    assert config["gtfs_output_name"] == "GTFS_Abidjan.zip"

    assert config["additional_tags_export"] == {
        "route": ["public_transport:version"],
        "stop_point": ["shelter"],
    }
