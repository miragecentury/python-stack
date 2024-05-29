#!/usr/bin/env bash

poetry run \
  pytest \
  --cov=src \
  --cov-report=lcov:build/coverage.lcov \
  --junitxml=build/junit.xml
