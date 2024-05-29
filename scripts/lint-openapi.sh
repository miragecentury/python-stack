#!/usr/bin/env bash

# Merge all OpenAPI files into a single file
redocly bundle docs/openapi/openapi.yml --output build/openapi.json

# Lint the merged OpenAPI file
redocly lint build/openapi.json
