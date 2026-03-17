#!/bin/bash

cd "$(dirname "$0")/../.." || exit 1

cd backend && python3 -m pytest tests/ -v -s --tb=long