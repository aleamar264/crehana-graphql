#!/bin/sh -e

set -x
alembic -c alembic_prod.ini upgrade head
python src/populate.py