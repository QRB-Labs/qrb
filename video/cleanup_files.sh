#!/bin/bash

# --- Argument Validation ---
# Check if exactly two arguments are provided.
if [ "$#" -ne 2 ]; then
    echo "Error: Incorrect number of arguments."
    echo "Usage: $0 <target_directory> <file_suffix>"
    echo "Example: $0 /var/log/videos .mp4"
    exit 1
fi

# Assign arguments to variables for clarity
TARGET_DIR="$1"
FILE_SUFFIX="$2"

# Check if the provided directory actually exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# --- Configuration ---
THRESHOLD=90                    # Percentage at which to start deleting
TARGET_FREE=85                  # Delete until disk usage drops back to this %

# Get current usage of the partition containing the target directory
CURRENT_USAGE=$(df "$TARGET_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$CURRENT_USAGE" -gt "$THRESHOLD" ]; then
    echo "Disk usage at ${CURRENT_USAGE}%. Cleaning up files with suffix '$FILE_SUFFIX' in '$TARGET_DIR'..."
    
    # Sort files by time (oldest first) and delete until usage is below TARGET_FREE
    while [ "$(df "$TARGET_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')" -gt "$TARGET_FREE" ]; do
        # Use find for a more robust and safe way to get the oldest file
        # -maxdepth 1: prevents searching in subdirectories
        # -type f: ensures we only find files
        # -printf '%T@ %p\n': prints modification time (unix epoch) and path
        # sort -n: sorts numerically (by epoch time)
        # cut: removes the timestamp
        # head -n 1: gets the top (oldest) one
        OLDEST_FILE=$(find "$TARGET_DIR" -maxdepth 1 -type f -name "*$FILE_SUFFIX" -printf '%T@ %p\n' 2>/dev/null | sort -n | head -n 1 | cut -d' ' -f2-)
        
        if [ -z "$OLDEST_FILE" ]; then
            echo "No more '$FILE_SUFFIX' files to delete."
            break
        fi
        
        echo "Deleting oldest file: $OLDEST_FILE"
        rm "$OLDEST_FILE"
    done
    echo "Cleanup complete. Usage now at $(df "$TARGET_DIR" | awk 'NR==2 {print $5}')."
else
    echo "Disk usage at ${CURRENT_USAGE}%. No cleanup needed."
fi
