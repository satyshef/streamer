from airflow import DAG
from airflow import models
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta
import os
import subprocess


# Ключевые настройки
DATA_DIR = './data'
INTERVAL = 120 # min
MIN_VIDEO_DURATION = 30 # какая минимальная длительность видео для стрима


VIDEO_SOURCE_PATH = "video/test"
#FILE_NAME = "stream_list/videolist_disposable.txt"
VIDEO_PATH = "stream_list/videolist_disposable.txt"
AUDIO_PATH = "stream_list/audiolist_dynamic.txt"

DAG_ID = "stream_dag"
KEY = "live_487176421_EcsFu6ZRH7WfHD5L72cobItWDTQjcQ"
URL = "rtmp://live.twitch.tv/app"



video_duration = 0
os.chdir(DATA_DIR)
# Устанавливаем target_datetime в начало текущего дня
today = datetime.now()
#.replace(hour=0, minute=0, second=0, microsecond=0)
target_datetime = today.strftime("%Y-%m-%d %H:%M:%S")

def create_video_playlist():
    global video_duration
    #video_duration = 0
    clip_duration = 9
    file_list = []
    # проверяем сумарную длительность видео
    for file in os.listdir(VIDEO_SOURCE_PATH):
        video_duration += clip_duration
        file_list.append(file)

    if video_duration < MIN_VIDEO_DURATION:
        print("Small video")
        raise AirflowSkipException
    
    # записываем в плейлист
    with open(VIDEO_PATH, 'w') as playlist_file:
        playlist_file.write('ffconcat version 1.0\n')
        playlist_file.write('file \'intro.mp4\'\n')
        for file in file_list:
            if file.endswith(".mp4"):  # adjust file extension as needed
                playlist_file.write(f"file '{VIDEO_SOURCE_PATH}/{file}'\n")
        #playlist_file.write("file 'videolist.txt'\n")


def run_ffmpeg_stream():
    ffmpeg_command = [
        "-re", "-f", "concat", "-safe", "0", "-i", VIDEO_PATH,
        "-f", "concat", "-i", AUDIO_PATH,
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
    
def cleanup_old_files():
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
    create_playlist_task = PythonOperator(
        task_id='create_video_playlist',
        python_callable=create_video_playlist,
        dag=dag,
    )

    cleanup_files_task = PythonOperator(
        task_id='cleanup_old_files',
        python_callable=cleanup_old_files,
        dag=dag,
    )

    #ffmpeg_command = 

    ffmpeg_stream_task = PythonOperator(
        task_id='ffmpeg_stream_task',
        python_callable=run_ffmpeg_stream,
        dag=dag,
    )

    #cleanup_files_task >> 
    create_playlist_task >> ffmpeg_stream_task >> cleanup_files_task
    #ffmpeg_stream_task