import json
from datasette import hookimpl
from .mvt import MVTServer
from .geojson import geojson_render
from .util import get_geo_column
from .inspect import get_spatial_tables, get_bounds


@hookimpl
def extra_js_urls(template, database, table, datasette):
    if get_geo_column(datasette, database, table) is not None:
        return [
            {"url": "https://api.tiles.mapbox.com/mapbox-gl-js/v0.54.0/mapbox-gl.js"},
            {"url": "/-/static-plugins/datasette_plugin_geo/main.js"},
        ]
    else:
        return []


@hookimpl
def extra_css_urls(template, database, table, datasette):
    if get_geo_column(datasette, database, table) is not None:
        return [
            {"url": "https://api.tiles.mapbox.com/mapbox-gl-js/v0.54.0/mapbox-gl.css"}
        ]
    else:
        return []


@hookimpl
def extra_body_script(template, database, table, datasette):
    if get_geo_column(datasette, database, table) is not None:
        bounds = datasette.inspect()[database]['geo']['bounds'][table]
        options = {
            "bounds": bounds,
            "database": database,
            "table": table,
        }
        return "geo_init_map({});".format(json.dumps(options))
    return ""


@hookimpl
def prepare_sanic(app, datasette):
    mvt = MVTServer(datasette)
    app.add_route(
        mvt.tile_endpoint, r"/-/tiles/<db_name:[^/]+>/<table:[^/]+?>/<z:int>/<x:int>/<y:int>.mvt"
    )
    app.add_route(
        mvt.tilejson_endpoint, r"/-/tiles/<db_name:[^/]+>/<table:[^/]+?>.json"
    )


@hookimpl
def inspect(database, conn):
    spatial_tables = get_spatial_tables(conn)
    return {
        "geo": {
            "spatial_tables": spatial_tables,
            "bounds": get_bounds(conn, spatial_tables),
        }
    }


@hookimpl
def register_output_renderer(datasette):
    return {
        'extension': 'geojson',
        'callback': lambda args, data, view_name: geojson_render(datasette, args, data, view_name)
    }
