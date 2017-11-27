#!/bin/bash

docker build -t tmpdist -f Dockerfile-dist .
docker run -dt --rm --name tmpdistrun tmpdist
mkdir -p dist
docker cp tmpdistrun:/dist/gateway ./dist
docker stop tmpdistrun
docker rmi tmpdist
