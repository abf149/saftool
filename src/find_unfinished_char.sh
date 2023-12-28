#!/bin/bash

# Define the destination directory
DEST_DIR="hw/sim_data"

# Find all log files in the directory
log_files=("$DEST_DIR"/*.log)

# Loop through each log file
for file in "${log_files[@]}"; do
    # Check if the file contains the text "Thank you" (case insensitive)
    if ! grep -iq "Thank you" "$file"; then
        # Output the name of the file if it does not contain the text
        echo "$file"
    fi
done
