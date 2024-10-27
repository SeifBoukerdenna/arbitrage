#!/bin/bash

# Find all Python files, excluding '__pycache__' and 'venv' directories, and display line counts along with filenames.
find . -name "*.py" ! -path "*/__pycache__/*" ! -path "*/venv/*" -exec wc -l {} + | tee /dev/tty | awk '{sum += $1} END {print "\nTotal Python lines:", sum}'
