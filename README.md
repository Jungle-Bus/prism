# Prism

Prism is a tool for extracting public transport routes from OpenStreetMap. It allows you to generate a GTFS feed from an OSM file.

## Use

`poetry run python prism/cli.py tests/data/osm/abidjan_test_data.osm.pbf --outdir out/ --loglevel=DEBUG`

`poetry run python prism/cli.py tests/data/osm/abidjan_test_data.osm.pbf --outdir out/ --loglevel=DEBUG --config example_config.json`

## Credits

This project has been developed by the [Jungle Bus](http://junglebus.io/) team.

The code in this repository is under the GPL-3.0 license.

This project uses OpenStreetMap data, licensed under the ODbL by the OpenStreetMap Foundation. You need to visibly credit OpenStreetMap and its contributors if you use or distribute the data generated from this project. Read more on [OpenStreetMap official website](https://www.openstreetmap.org/copyright).

![Jungle Bus Logo](https://github.com/Jungle-Bus/resources/raw/master/logo/Logo_Jungle_Bus.png)

## See also

This project is heavily inspired by the following previous projects:
* https://github.com/grote/osm2gtfs
* https://github.com/hiposfer/o2g
* https://github.com/CanalTP/osm-transit-extractor

Big thanks to their open source contributors :sparkling_heart:
