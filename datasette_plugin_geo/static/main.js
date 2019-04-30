function geo_init_map(options) {
  let style = {
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
    },
    layers: [
      {
        id: 'openstreetmap',
        type: 'raster',
        source: 'openstreetmap',
        minzoom: 0,
        maxzoom: 22,
      },
    ],
  };

  if (options['view_name'] == 'table') {
    style['sources']['datasette'] = {
      type: 'vector',
      url: '/-/tiles/' + options['database'] + '/' + options['table'] + '.json',
    };

    style['layers'].push({
        id: 'datasette_point',
        type: 'circle',
        source: 'datasette',
        filter: ['==', ['geometry-type'], 'Point'],
        'source-layer': options['table'],
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 8, 2, 10, 5],
          'circle-stroke-width': [
            'interpolate',
            ['linear'],
            ['zoom'],
            6,
            0,
            10,
            2,
          ],
          'circle-color': '#6B7AE8',
          'circle-stroke-color': '#999999',
        },
      });
    initMap(options, style, new mapboxgl.LngLatBounds(
      [options['bounds'][0], options['bounds'][1]],
      [options['bounds'][2], options['bounds'][3]],
    ));
  } else if (options['view_name'] == 'row') {
    fetch(window.location.href + ".geojson").then(response => response.json()).then(geojson => {
    style['sources']['point_geojson'] = {
      type: 'geojson',
      data: geojson,
    };

    style['layers'].push({
        id: 'datasette_point',
        type: 'circle',
        source: 'point_geojson',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 8, 2, 10, 5],
          'circle-stroke-width': [
            'interpolate',
            ['linear'],
            ['zoom'],
            6,
            0,
            10,
            2,
          ],
          'circle-color': '#6B7AE8',
          'circle-stroke-color': '#999999',
        },
      });
      var bounds = new mapboxgl.LngLatBounds();
      bounds.extend(geojson.geometry.coordinates);
      initMap(options, style, bounds);
    })
  }
}

function initMap(options, style, bounds) {
  var map_container = document.getElementById('datasette-geo-map');
  map_container.style.width = '100%';
  map_container.style.height = '500px';
  var map = new mapboxgl.Map({
    container: 'datasette-geo-map',
    style: style,
    bounds: bounds,
    fitBoundsOptions: {maxZoom: 10}
  });
  register_popup(options, map, 'datasette_point');
}

function register_popup(options, map, layer) {
  map.on('click', layer, e => {
    var coordinates = e.features[0].geometry.coordinates.slice();
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }
    var url = `/${options['database']}/${options['table']}/${
      e.features[0].properties['uid'] || e.features[0].properties['id']
    }`;
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
