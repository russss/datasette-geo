import json
import shapely.geometry
from .util import get_geo_column, from_spatialite_geom


def row_to_feature(row, geo_column):
    return {
        "type": "Feature",
        "geometry": shapely.geometry.mapping(from_spatialite_geom(row[geo_column])),
        "properties": {key: row[key] for key in row.keys() if key != geo_column},
    }


def geojson_render(datasette, args, data, view_name):
    if view_name not in ("row", "table"):
        return None

    geo_column = get_geo_column(datasette, data["database"], data["table"])
    if geo_column is None:
        return None

    if view_name == "row":
        gj = row_to_feature(data["rows"][0], geo_column)
    elif view_name == "table":
        gj = {
            "type": "FeatureCollection",
            "features": [row_to_feature(row, geo_column) for row in data["rows"]],
        }
        for k, v in data.items():
            if k != 'rows':
                gj[k] = v

    return {"content_type": "application/vnd.geo+json", "body": json.dumps(gj)}
