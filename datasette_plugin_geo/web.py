import mapbox_vector_tile
import mercantile
import shapely.geometry
from sanic import response
from sanic.exceptions import NotFound

from .util import get_geo_column


def valid_zoom(z):
    return 0 <= z <= 17


def valid_lat(lat):
    return -90 <= lat <= 90


def valid_lon(lon):
    return -180 <= lon <= 180


def valid_bounds(bounds):
    return (
        valid_lon(bounds.east)
        and valid_lon(bounds.west)
        and valid_lat(bounds.north)
        and valid_lat(bounds.south)
    )


def polygon_from_bounds(bounds):
    return shapely.geometry.box(bounds.east, bounds.south, bounds.west, bounds.north)


def spatial_index_query(table, bbox):
    return """SELECT ROWID FROM SpatialIndex
                WHERE f_table_name = '{table}'
                AND search_frame = GeomFromText('{bbox}')""".format(
        table=table, bbox=bbox.wkt
    )


class MVTServer(object):
    def __init__(self, datasette):
        self.datasette = datasette

    def feature_from_row(self, row):
        return {"geometry": row["geom"], "properties": {"uid": row[0]}}

    def layer_from_result(self, name, res):
        return {"name": name, "features": [self.feature_from_row(row) for row in res]}

    async def get_features(self, db_name, table, geo_column, z, x, y):
        bounds = mercantile.bounds(x, y, z)
        if not valid_bounds(bounds):
            raise NotFound("Tile coordinates out of bounds")

        sql = """SELECT ROWID, *, AsText(Transform({geo_column}, 3857)) AS geom
                 FROM {table} WHERE ROWID IN ({index_query})""".format(
            table=table,
            geo_column=geo_column,
            index_query=spatial_index_query(table, polygon_from_bounds(bounds)),
        )
        res = await self.datasette.execute(db_name, sql)

        return [self.layer_from_result(table, res)]

    async def tile_endpoint(self, request, db_name, table, z, x, y):
        if not valid_zoom(z):
            raise NotFound("Invalid zoom value")
        if not self.datasette.table_exists(db_name, table):
            raise NotFound("Table does not exist")
        geo_column = get_geo_column(self.datasette, db_name, table)
        if geo_column is None:
            raise NotFound("Not a spatial table")

        mvt = mapbox_vector_tile.encode(
            await self.get_features(db_name, table, geo_column, z, x, y),
            quantize_bounds=mercantile.xy_bounds(x, y, z),
        )

        return response.raw(
            mvt, headers={"Content-Type": "application/vnd.mapbox-vector-tile"}
        )

    async def tilejson_endpoint(self, request, db_name, table):
        # TODO: expose name/attribution metadata here
        if not self.datasette.table_exists(db_name, table):
            raise NotFound("Table does not exist")
        geo_column = get_geo_column(self.datasette, db_name, table)
        if geo_column is None:
            raise NotFound("Not a spatial table")
        bounds = self.datasette.inspect()[db_name]['geo']['bounds'][table]

        return response.json({
            "tilejson": "2.2.0",
            "name": "Datasette Geo",
            "attribution": "TODO",
            "bounds": bounds,
            "center": [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, 0],
            "minzoom": 0,
            "maxzoom": 17,
            "tiles": [
                "{scheme}://{host}/-/tiles/{db_name}/{table}/{{z}}/{{x}}/{{y}}.mvt".format(
                    scheme=request.scheme, host=request.host, db_name=db_name, table=table
                )
            ]
        })
