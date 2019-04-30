from shapely import wkb
from functools import lru_cache


@lru_cache()
def get_geo_column(datasette, database, table):
    if database is None or table is None:
        return None
    insp = datasette.inspect()
    if "geo" not in insp[database]:
        # This shouldn't happen, as our inspect hook always gets called, but
        # it does currently happen when running the main datasette tests.
        return None
    return insp[database]["geo"]["spatial_tables"].get(table)


def from_spatialite_geom(geom):
    if geom is None:
        return None
    # Eviscerate the ridiculous Spatialite binary geometry format
    # and reassemble it into something which hopefully looks like WKB.
    #
    # This has been tested with points only but I don't see any reason
    # why it wouldn't work with other geometries. It probably won't work with
    # Spatialite TinyPoints.
    return wkb.loads(geom[1:2] + geom[39:43] + geom[43:-1])
