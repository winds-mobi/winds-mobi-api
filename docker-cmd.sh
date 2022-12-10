#!/usr/bin/env bash

if [[ $TELEMETRY_DISABLED ]]; then
  uvicorn --proxy-headers --root-path "$ROOT_PATH" --host 0.0.0.0 --port "$PORT" winds_mobi_api.main:app
else
  opentelemetry-instrument --traces_exporter otlp uvicorn --proxy-headers --root-path "$ROOT_PATH" --host 0.0.0.0 --port "$PORT" winds_mobi_api.main:app
fi
