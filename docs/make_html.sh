#!/bin/bash

# Prevent saftools from running on import
export SPHINX_BUILD=1

# Run Sphinx build
make html