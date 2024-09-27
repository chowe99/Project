#!/bin/bash

cd /opt/docslair

docker compose down
docker compose up --build
