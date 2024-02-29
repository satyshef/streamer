#/bin/bash

VIDEO_PATH="videolist.txt"
AUDIO_PATH="audiolist.txt"
WORK_DIR="/root/config/streamer/"

KEY="jww0-gred-8vfj-tduk-fa13"
URL="rtmp://a.rtmp.youtube.com/live2"

cd $WORK_DIR
ffmpeg -re -f concat -safe 0 -i $VIDEO_PATH -f concat -i $AUDIO_PATH -c:v copy -c:a copy -f flv -g 60 -flvflags no_duration_filesize $URL/$KEY