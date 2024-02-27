import subprocess

KEY = "jww0-gred-8vfj-tduk-fa13"
VIDEO_PATH = "/root/config/streamer/videolist.txt"
AUDIO_PATH = "/root/config/streamer/audiolist.txt"
# AUDIO_PATH="video/test.mp3"
# VIDEO_PATH="video/stream_base.mp4"
URL = "rtmp://a.rtmp.youtube.com/live2"

command = [
    "ffmpeg",
    "-re",
    "-f", "concat",
    "-i", VIDEO_PATH,
    "-f", "concat",
    "-i", AUDIO_PATH,
    "-c:v", "copy",
    "-c:a", "copy",
    "-f", "flv",
    "-g", "60",
    f"{URL}/{KEY}"
]

subprocess.run(command)
