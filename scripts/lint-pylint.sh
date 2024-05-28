#!/usr/bin/env bash

pylint \
  --fail-under=9.5 \
  --output-format=colorized \
  --rcfile=pylintrc src/
