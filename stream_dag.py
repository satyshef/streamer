from airflow import DAG
from airflow import models
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta
import os

# Ключевые настройки
DATA_DIR = './data'
INTERVAL = 60 # min
MIN_VIDEO_DURATION = 90 # какая минимальная длительность видео для стрима в секундах


VIDEO_SOURCE_PATH = "video/test"
VIDEO_PLAYLIST = "stream_list/videolist_disposable.txt"
AUDIO_PLAYLIST = "stream_list/audiolist_dynamic.txt"

DAG_ID = "stream_dag"
#youtube
KEY="jww0-gred-8vfj-tduk-fa13"
URL="rtmp://a.rtmp.youtube.com/live2"
# twitch
#KEY = "live_487176421_EcsFu6ZRH7WfHD5L72cobItWDTQjcQ"
#URL = "rtmp://live.twitch.tv/app"



#video_duration = 0
os.chdir(DATA_DIR)
# Устанавливаем target_datetime в начало текущего дня
today = datetime.now()
#.replace(hour=0, minute=0, second=0, microsecond=0)
target_datetime = today.strftime("%Y-%m-%d %H:%M:%S")

@task.python
def create_video_playlist(video_dir, playlist_path):
    file_list = []
    # проверяем сумарную длительность видео
    for file in os.listdir(video_dir):
        file_list.append(file)
 
    # записываем в плейлист
    with open(playlist_path, 'w') as playlist_file:
        playlist_file.write('ffconcat version 1.0\n')
        playlist_file.write('file \'intro.mp4\'\n')
        for file in file_list:
            if file.endswith(".mp4"):  # adjust file extension as needed
                playlist_file.write(f"file '{video_dir}/{file}'\n")
        #playlist_file.write("file 'videolist.txt'\n")
                
    return file_list


# переделать так что бы загружадась реальная длитильность клипа
@task.python
def calc_video_duration(file_list):
    clip_duration = 9
    video_duration = clip_duration * len(file_list)
    #for file in file_list:
    #  video_duration += clip_duration

    if video_duration < MIN_VIDEO_DURATION:
        print("Small video")
        raise AirflowSkipException
    
    return video_duration

@task.python
def run_ffmpeg_stream(video_playlist, audio_playlist, video_duration):
    ffmpeg_command = [
        "-re", "-f", "concat", "-safe", "0", "-i", video_playlist,
        "-f", "concat", "-i", audio_playlist,
        "-c:v", "copy", "-c:a", "copy",
        "-f", "flv", "-g", "60", "-t", str(video_duration),
        "-flvflags", "no_duration_filesize", f"{URL}/{KEY}"
    ]
    
    docker_task = DockerOperator(
        task_id='ffmpeg_docker_task',
        image='jrottenberg/ffmpeg:4.1-ubuntu',
        api_version='auto',
        auto_remove=True,
        command=ffmpeg_command,
        docker_url="unix://var/run/docker.sock",
        mount_tmp_dir=False,
        working_dir='/root/data',
        mounts=[{
            'source': '/root/data',
            'target': '/root/data',
            "type": "bind"
        }],
    )
    
    return docker_task.execute(context=None)
    
@task.python
def delete_used_files(file_list):
    for file in file_list:
        os.remove(file)
    return
    os.system(f"find '{VIDEO_SOURCE_PATH}' -type f ! -newermt '{target_datetime}' -exec rm {{}} \;")
    print("Old files deleted.")


with models.DAG(
    DAG_ID,
    schedule=timedelta(minutes=INTERVAL),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["polihoster", "streamer", "test"],
) as dag:
    
    create_playlist_task = create_video_playlist(VIDEO_SOURCE_PATH, VIDEO_PLAYLIST)
    video_duration_task = calc_video_duration(create_playlist_task)
    ffmpeg_task = run_ffmpeg_stream(VIDEO_PLAYLIST, AUDIO_PLAYLIST, video_duration_task)
    delete_files_task = delete_used_files(create_playlist_task)

    create_playlist_task >> video_duration_task >> ffmpeg_task >> delete_files_task

    #cleanup_files_task >> 
    #create_playlist_task >> ffmpeg_stream_task >> cleanup_files_task
    #ffmpeg_stream_task