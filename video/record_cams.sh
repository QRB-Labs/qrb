#!/bin/bash

# ffmpeg -rtsp_transport tcp -i rtsp://$CAMERA_USER:$CAMERA_PASSWORD@cam1.qrb-labs.com:554/ch01_sub -c:v copy -c:a aac -f segment -segment_time 300 -strftime 1 "/tmp/cam1_%Y%m%d_%H%M%S.mp4" > /tmp/ffmpeg_stdout.log 2> /tmp/ffmpeg_stderr.log

# Define your cameras and their RTSP URLs
# Format: "name|url"
CAMERAS=(
  "cam1|rtsp://$CAMERA_USER:$CAMERA_PASSWORD@cam1.qrb-labs.com:554/ch01_sub"
  "cam2|rtsp://$CAMERA_USER:$CAMERA_PASSWORD@cam2.qrb-labs.com:554/ch01_sub"
  "cam3|rtsp://$CAMERA_USER:$CAMERA_PASSWORD@cam3.qrb-labs.com:554/ch01_sub"
  "cam4|rtsp://$CAMERA_USER:$CAMERA_PASSWORD@cam4.qrb-labs.com:554/ch01_sub"
  "cam5|rtsp://$CAMERA_USER:$CAMERA_PASSWORD@cam5.qrb-labs.com:554/ch01_sub"
)

RECORD_DIR="/tmp/video" # Change to EBS mount point

# Function to record a single camera
record_camera() {
    local name=$1
    local url=$2
    
    echo "Starting recording for $name..." | logger -t "ffmpeg-$name"
    
    # The 'while true' loop handles stream interruptions
    while true; do
        ffmpeg -loglevel warning -rtsp_transport tcp -i "$url" \
        -c:v copy -c:a aac \
        -f segment -segment_time 300 -strftime 1 \
        -reset_timestamps 1 \
        "$RECORD_DIR/%Y%m%d_%H%M%S_${name}.mp4" 2>&1 | logger -t "ffmpeg-$name"
        
        echo "Camera $name disconnected. Retrying in 5 seconds..." | logger -t "ffmpeg-$name"
        sleep 5
    done
}

# Loop through the array and start each recording in the background
for entry in "${CAMERAS[@]}"; do
    IFS="|" read -r cam_name cam_url <<< "$entry"
    record_camera "$cam_name" "$cam_url" &
done

# Keep the script alive so the background processes don't die
wait
