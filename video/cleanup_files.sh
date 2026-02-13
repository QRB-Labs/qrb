#!/bin/bash

# Configuration
FILE_SUFFIX=".mp4"
TARGET_DIR="/tmp/video"              # Where your .mp4 files are
THRESHOLD=33                    # Percentage at which to start deleting
TARGET_FREE=32                  # Delete until disk usage drops back to this %

# Get current usage of the partition containing the target directory
CURRENT_USAGE=$(df "$TARGET_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$CURRENT_USAGE" -gt "$THRESHOLD" ]; then
    echo "Disk usage at ${CURRENT_USAGE}%. Cleaning up..."
    
    # Sort files by time (oldest first) and delete until usage is below TARGET_FREE
    while [ "$(df "$TARGET_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')" -gt "$TARGET_FREE" ]; do
        OLDEST_FILE=$(ls -1tr "$TARGET_DIR"/*"$FILE_SUFFIX" 2>/dev/null | head -n 1)
        
        if [ -z "$OLDEST_FILE" ]; then
            echo "No more $FILE_SUFFIX files to delete."
            break
        fi
        
        echo "Deleting oldest file: $OLDEST_FILE"
        rm "$OLDEST_FILE"
    done
    echo "Cleanup complete. Usage now at $(df "$TARGET_DIR" | awk 'NR==2 {print $5}')."
else
    echo "Disk usage at ${CURRENT_USAGE}%. No cleanup needed."
fi
