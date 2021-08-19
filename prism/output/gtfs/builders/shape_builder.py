from prism.misc.models import ShapePoint


def build_shapes(geom):
    for osm_route_id, osm_geom in geom.items():
        for index, latlon in enumerate(osm_geom):
            yield ShapePoint(osm_route_id, latlon.lat, latlon.lon, index)
