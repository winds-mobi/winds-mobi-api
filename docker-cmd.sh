#!/usr/bin/env bash

if [[ $TELEMETRY_DISABLED ]]; then
  uvicorn --log-config=winds_mobi_api/logging.yaml --proxy-headers --root-path="$ROOT_PATH" --host=0.0.0.0 --port="$PORT" winds_mobi_api.main:app
else
  opentelemetry-instrument --metrics_exporter=none uvicorn --log-config=winds_mobi_api/logging.yaml --proxy-headers --root-path="$ROOT_PATH" --host=0.0.0.0 --port="$PORT" winds_mobi_api.main:app
fi
