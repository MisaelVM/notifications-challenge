#!/bin/sh

docker compose --profile test --env-file .env.test build && \
docker compose --profile test --env-file .env.test up
