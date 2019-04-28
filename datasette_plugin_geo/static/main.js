function geo_init_map(options) {
  var style = {
    version: 8,
    name: 'Datasette Geo',
    sources: {
      openstreetmap: {
        type: 'raster',
        tiles: [
          'http://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'http://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'http://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
        ],
        tileSize: 256,
      },
      datasette: {
        type: 'vector',
        url: '/-/tiles/' + options['database'] + '/' + options['table'] + '.json'
      }
    },
    layers: [
      {
        id: 'openstreetmap',
        type: 'raster',
        source: 'openstreetmap',
        minzoom: 0,
        maxzoom: 22,
      },
      {
        id: 'datasette',
        type: 'circle',
        source: 'datasette',
        "source-layer": options['table'],
        paint: {
          'circle-color': "#ff0000",
        }
      }
    ],
  };

  var map_container = document.getElementById('datasette-geo-map');
  map_container.style.width = '1000px';
  map_container.style.height = '500px';
  var map = new mapboxgl.Map({
    container: 'datasette-geo-map',
    style: style,
    bounds: new mapboxgl.LngLatBounds(
      [options['bounds'][0], options['bounds'][1]],
      [options['bounds'][2], options['bounds'][3]],
    ),
  });
}
