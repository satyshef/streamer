#/bin/bash

KEY="live_487176421_EcsFu6ZRH7WfHD5L72cobItWDTQjcQ"
VIDEO_PATH="looplist.txt"
AUDIO_PATH="audiolist.txt"

ffmpeg -re -f concat -safe 0 -i $VIDEO_PATH -f concat -i $AUDIO_PATH -c:v copy -c:a copy -f flv -g 60 -flvflags no_duration_filesize $URL/$KEY