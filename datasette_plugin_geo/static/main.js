const point_layer_paint = {
  'circle-radius': ['interpolate', ['linear'], ['zoom'], 8, 2, 10, 5],
  'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 6, 0, 10, 2],
  'circle-color': '#6B7AE8',
  'circle-stroke-color': '#999999',
};

var datasette_geo_layers_added = false;

function geo_init_map(options) {
  mapboxgl.accessToken = options['mapbox_token'];
  var map_container = document.getElementById('datasette-geo-map');
  map_container.style.width = '100%';
  map_container.style.height = '500px';
  var map = new mapboxgl.Map({
    container: 'datasette-geo-map',
    style: options['style'],
    fitBoundsOptions: {maxZoom: 10},
    bounds: new mapboxgl.LngLatBounds(
      [options['bounds'][0], options['bounds'][1]],
      [options['bounds'][2], options['bounds'][3]],
    ),
  });

  // We need to wait for initial style to load before we add our own layers.
  // But this callback gets called on every style change so make sure it's
  // only called once.
  map.on('styledata', e => {
    if (!datasette_geo_layers_added) {
      datasette_geo_layers_added = true;
      add_datasette_layers(options, map);
    }
  });
}

function add_datasette_layers(options, map) {
  register_popup(options, map, 'datasette_point');

  if (options['view_name'] == 'table') {
    map.addSource('datasette', {
      type: 'vector',
      url: '/-/tiles/' + options['database'] + '/' + options['table'] + '.json',
    });

    var style = map.getStyle();
    style['layers'].push({
      id: 'datasette_point',
      type: 'circle',
      source: 'datasette',
      filter: ['==', ['geometry-type'], 'Point'],
      'source-layer': options['table'],
      paint: point_layer_paint,
    });
    map.setStyle(style);
  } else if (options['view_name'] == 'row') {
    fetch(window.location.href + '.geojson')
      .then(response => response.json())
      .then(geojson => {
        map.addSource('datasette_point', {
          type: 'geojson',
          data: geojson,
        });

        var style = map.getStyle();
        style['layers'].push({
          id: 'datasette_point',
          type: 'circle',
          source: 'datasette_point',
          paint: point_layer_paint,
        });
        map.setStyle(style);

        var bounds = new mapboxgl.LngLatBounds();
        bounds.extend(geojson.geometry.coordinates);
        map.fitBounds(bounds, {maxZoom: 10});
      });
  }
}

function register_popup(options, map, layer) {
  map.on('click', layer, e => {
    var coordinates = e.features[0].geometry.coordinates.slice();
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }
    var url = `/${options['database']}/${options['table']}/${e.features[0]
      .properties['uid'] || e.features[0].properties['id']}`;
    fetch(url + '.json')
      .then(response => response.json())
      .then(data => {
        new mapboxgl.Popup({className: 'datasette-geo-popup'})
          .setLngLat(coordinates)
          .setHTML(render_popup(data, url))
          .addTo(map);
      });
  });

  map.on('mouseenter', layer, function() {
    map.getCanvas().style.cursor = 'pointer';
  });

  map.on('mouseleave', layer, function() {
    map.getCanvas().style.cursor = '';
  });
}

function render_popup(data, url) {
  var html = `<a href="${url}">View Row</a>`;

  html += '<div class="datasette-geo-data">';
  for (var i = 0; i < data.rows[0].length; i++) {
    if (typeof data.rows[0][i] != 'object') {
      html += `<div>
                <div class="datasette-geo-key">${data.columns[i]}</div>
                <div class="datasette-geo-value">${data.rows[0][i]}</div>
               </div>`;
    }
  }
  html += '</div>';
  return html;
}
