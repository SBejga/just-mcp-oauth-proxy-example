#! /bin/bash
ENV_FILE="${1:-./.env}"
op run --env-file "$ENV_FILE" -- ./.venv/bin/python $2