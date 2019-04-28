
def get_geo_column(datasette, database, table):
    if database is None or table is None:
        return None
    insp = datasette.inspect()
    return insp[database]['geo']['spatial_tables'].get(table)
