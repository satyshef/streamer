import subprocess

KEY = "jww0-gred-8vfj-tduk-fa13"
#VIDEO_PATH = "/root/config/streamer/videolist.txt"
VIDEO_PATH = "/tmp/videostream"
AUDIO_PATH = "/root/config/streamer/audiolist.txt"
URL = "rtmp://a.rtmp.youtube.com/live2"

subprocess.run(["mkfifo", VIDEO_PATH])

command = [
    "ffmpeg",
    "-re",
    "-i", VIDEO_PATH,
    "-f", "concat",
    "-i", AUDIO_PATH,
    "-c:v", "copy",
    "-c:a", "copy",
    "-f", "flv",
    "-g", "60",
    f"{URL}/{KEY}"
]

while True:
    subprocess.run(command)
