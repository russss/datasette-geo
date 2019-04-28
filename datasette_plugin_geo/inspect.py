from datasette import hookimpl
from shapely import wkt


def get_spatial_tables(conn):
    spatial_tables = {}

    c = conn.cursor()
    c.execute(
        """SELECT f_table_name, f_geometry_column, srid, spatial_index_enabled
                 FROM geometry_columns"""
    )
    for row in c.fetchall():
        if row[3] != 1:
            print(
                "Column {column} in table {table} has no spatial index; datasette-geo will ignore it.".format(
                    column=row[1], table=row[0]
                )
            )
            continue
        spatial_tables[row[0]] = row[1]
    return spatial_tables


def get_bounds(conn, spatial_tables):
    c = conn.cursor()
    res = {}
    for table, column in spatial_tables.items():
        c.execute(
            "SELECT AsText(Envelope(GUnion({column}))) FROM {table}".format(
                table=table, column=column
            )
        )
        bbox = wkt.loads(c.fetchone()[0])
        res[table] = bbox.bounds
    return res
