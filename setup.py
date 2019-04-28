from setuptools import setup

VERSION = '0.1'

setup(
    name='datasette-geo',
    description='TODO',
    author='Russ Garrett',
    url='TODO',
    license='Apache License, Version 2.0',
    version=VERSION,
    py_modules=['datasette_plugin_geo'],
    entry_points={
        'datasette': [
            'plugin_geo = datasette_plugin_geo'
        ]
    },
    install_requires=['datasette']
)
