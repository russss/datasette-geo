osm_raster = {
  'version': 8,
  'name': 'Datasette Geo',
  'sources': {
    'openstreetmap': {
      'type': 'raster',
      'tiles': [
        'http://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'http://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'http://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
      ],
      'tileSize': 256,
      'attribution': '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
  },
  'layers': [
    {
      'id': 'openstreetmap',
      'type': 'raster',
      'source': 'openstreetmap',
      'minzoom': 0,
      'maxzoom': 22,
    },
  ],
}
