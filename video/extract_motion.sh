#!/bin/bash

# Configuration
SOURCE_DIR="/tmp/video"  # All videos are directly here
MODELS_DIR="/tmp/video_frames"
# Sensitivity: 0.05 = 5% change. Lower = more sensitive.
SENSITIVITY="0.05"

mkdir -p "$MODELS_DIR"

# Find all eligible MP4 files directly in SOURCE_DIR
# Changed -mmin +1 to -mmin +5 to ensure files are truly completed and not being written to.
find "$SOURCE_DIR" -maxdepth 1 -name "*.mp4" -mmin +5 -mmin -65 -print0 | while IFS= read -r -d $'\0' LATEST_FILE; do
    if [ -z "$LATEST_FILE" ]; then
	echo "No new files found in $SOURCE_DIR."
	continue
    fi

    echo $LATEST_FILE
    # Extract the filename without the path
    FILENAME=$(basename "$LATEST_FILE")

    # Filename format: YYYYMMMDD_HHMMSS_camX.mp4
    # Extract 'YYYYMMMDD_HHMMSS' and 'camX'.
    if [[ "$FILENAME" =~ ^([0-9]+_[0-9]+)_([^.]+)\.mp4$ ]]; then
	TIMESTAMP_PART="${BASH_REMATCH[1]}"
	CAMERA_ID="${BASH_REMATCH[2]}"
    else
	echo "Warning: Filename '$FILENAME' does not match expected format. Skipping."
	continue # Skip this file if it doesn't match the expected format
    fi

    echo "Processing file: $FILENAME (Timestamp: $TIMESTAMP_PART, Camera: $CAMERA_ID)" | logger -t "extract_motion"

    # Extract frames where motion is detected
    # Modified output path to include TIMESTAMP_PART
    ffmpeg -loglevel error -i "$LATEST_FILE" \
    -vf "select='gt(scene,$SENSITIVITY)',setpts=N/FRAME_RATE/TB" \
    -vsync vfr -q:v 2 "$MODELS_DIR/${TIMESTAMP_PART}_${CAMERA_ID}_%03d.jpg"

    echo "Done with file '$FILENAME'. Frames saved to $MODELS_DIR" | logger -t "extract_motion"
done
