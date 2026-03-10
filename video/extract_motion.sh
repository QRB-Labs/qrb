#!/bin/bash

# Configuration
SOURCE_DIR="/tmp/video"  # All videos are directly here
MODELS_DIR="/tmp/video_frames"
# Sensitivity: 0.05 = 5% change. Lower = more sensitive.
SENSITIVITY="0.05"

mkdir -p "$MODELS_DIR"

# Find eligible files: MP4 files in SOURCE_DIR, modified more than 5
# and less than 65 minutes ago.
# Use mapfile (aka readarray) to safely read the NUL-delimited output from find
# into the 'files' array.
# < <(...) is process substitution, which avoids creating a subshell for the read.
files=()
mapfile -d $'\0' files < <(find "$SOURCE_DIR" -maxdepth 1 -name "*.mp4" -mmin +5 -mmin -65 -print0)

if [ ${#files[@]} -eq 0 ]; then
    echo "No new files found in $SOURCE_DIR." | logger -t "extract_motion"
    exit 0
fi

echo "Found ${#files[@]} file(s) to process." | logger -t "extract_motion"

for LATEST_FILE in "${files[@]}"; do
    # Extract the filename without the path
    FILENAME=$(basename "$LATEST_FILE")

    # Filename format: YYYYMMMDD_HHMMSS_camX.mp4
    # Extract 'YYYYMMMDD_HHMMSS' and 'camX'.
    if [[ "$FILENAME" =~ ^([0-9]+_[0-9]+)_([^.]+)\.mp4$ ]]; then
	TIMESTAMP_PART="${BASH_REMATCH[1]}"
	CAMERA_ID="${BASH_REMATCH[2]}"
    else
	echo "Warning: Filename '$FILENAME' does not match expected format. Skipping." | logger -t "extract_motion"
	continue # Skip this file if it doesn't match the expected format
    fi

    echo "Processing $LATEST_FILE -> $FILENAME -> Timestamp: $TIMESTAMP_PART, Camera: $CAMERA_ID)" | logger -t "extract_motion"

    # Extract frames where motion is detected
    # Modified output path to include TIMESTAMP_PART
    (ffmpeg -loglevel error -i "$LATEST_FILE" \
    -vf "select='gt(scene,$SENSITIVITY)',setpts=N/FRAME_RATE/TB" \
    -vsync vfr -q:v 2 "$MODELS_DIR/${TIMESTAMP_PART}_${CAMERA_ID}_%03d.jpg"
     ) < /dev/null 2>&1 | logger -t "extract_motion" -p user.error

    echo "Done with '$LATEST_FILE'. Frames saved to $MODELS_DIR" | logger -t "extract_motion"
done
