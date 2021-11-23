#!/usr/bin/env sh

until nc -z "$ELASTIC_HOST" "$ELASTIC_PORT"; do
  >&2 echo "Waiting for elastic..."
  sleep 1
done

exec "$@"
