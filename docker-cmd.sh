#!/usr/bin/env sh

opentelemetry-instrument --traces_exporter otlp uvicorn --proxy-headers --root-path "$ROOT_PATH" --host 0.0.0.0 --port "$PORT" winds_mobi_api.main:app
