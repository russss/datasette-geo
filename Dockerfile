FROM datasette-russss:latest

COPY . /datasette-geo
RUN pip install /datasette-geo; rm -Rf /datasette-geo
