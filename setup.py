from setuptools import setup

VERSION = '0.1'

setup(
    name='datasette-geo',
    description='A Datasette plugin to make Spatialite databases effortlessly explorable',
    author='Russ Garrett',
    url='https://github.com/russss/datasette-geo',
    license='Apache License, Version 2.0',
    version=VERSION,
    packages=['datasette_plugin_geo'],
    package_data={
        'datasette_plugin_geo': [
            'static/*',
            'templates/*.html'
        ]
    },
    entry_points={
        'datasette': [
            'plugin_geo = datasette_plugin_geo'
        ]
    },
    install_requires=[
        'datasette',
        'shapely',
        'mapbox_vector_tile',
        'mercantile',
    ]
)
