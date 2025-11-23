#!/bin/bash
#
# Valuation App - Quick Start Script
# This script can be run from ANY directory and will work correctly
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project root
cd "$SCRIPT_DIR"

# Run the actual start-servers script
exec bash scripts/server/start-servers.sh
