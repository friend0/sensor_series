Panopticon OPC + Web Application + MongoDB
===========================================

Building with Docker
---------------------

To build the web application and OPC by itself (one might want to do this for debugging reasons),
do:

$ cd path/to/panopticon
$ docker build -t panopticon .
$ docker run -i -t panopticon:latest

The preceding commands will:
- Build the docker container (happens from project root directory)
- Run the container

In order to run the application container WITH the mongoDB container, we need to work with docker-compose.
Still in the root directory:

$ docker-compose build
$ docker-compose up

To run in detached mode (containers run in background instead of shell):

$ docker-compose build
$ docker-comopse up -d

You can see the detached processes by doing:

$ docker-compose ps

Read the docker-compose reference here:
https://docs.docker.com/compose/reference/overview/
