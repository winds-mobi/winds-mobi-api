#!/usr/bin/env sh

uvicorn --proxy-headers --root-path "$ROOT_PATH" --host 0.0.0.0 --port 8000 winds_mobi_api.main:app
