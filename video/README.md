Scripts to 
- record from RTSP streams to video clip files
- detect motion/change in video and save to image files
- manage files within a % of available disk space

Assumes
- Environment variables: CAMER_USER and CAMERA_PASSWORD
- Configure TARGET_DIR in scripts to eg. your video drive mount point
- ffmpeg. version > 6. https://github.com/BtbN/FFmpeg-Builds/releases

TODO
- real time view page via websocket
- RTSP relay: go2rtc https://github.com/AlexxIT/go2rtc?tab=readme-ov-file#go2rtc-binary
