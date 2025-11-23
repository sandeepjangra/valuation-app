#!/bin/bash
#
# Valuation App - Quick Stop Script
# This script can be run from ANY directory and will work correctly
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project root
cd "$SCRIPT_DIR"

# Run the actual stop-servers script
exec bash scripts/server/stop-servers.sh
