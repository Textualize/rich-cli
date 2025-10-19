#!/bin/bash

set -e

if [ "$1" == "base" ]; then
    echo "Running base tests..."
    python -m pytest tests/ -k "not ansi_preprocessing"
elif [ "$1" == "new" ]; then
    echo "Running new tests..."
    python -m pytest tests/test_ansi_preprocessing.py -v
else
    echo "Usage: ./test.sh [base|new]"
    echo "  base - Run existing tests (excluding ANSI preprocessing tests)"
    echo "  new  - Run ANSI preprocessing tests"
    exit 1
fi




			
		







