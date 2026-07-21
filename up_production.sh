#!/bin/sh

docker compose --profile production --env-file .env build
docker compose --profile production --env-file .env up
