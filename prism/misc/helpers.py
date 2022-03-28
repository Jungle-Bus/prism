from math import cos, sin, atan2, sqrt, radians


def crow_fly_distance(lon1, lat1, lon2, lat2):
    """
    Uses the Haversine formmula to compute distance
    (https://en.wikipedia.org/wiki/Haversine_formula#The_haversine_formula)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    radius = 6371  # km
    a = sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(
        dlon / 2
    ) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = radius * c

    return d * 1000  # meters
