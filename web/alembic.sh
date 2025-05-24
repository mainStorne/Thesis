#!/bin/bash

echo "Применение миграций"
sleep 20s # wait when db is ready
alembic upgrade head

exec "$@"
