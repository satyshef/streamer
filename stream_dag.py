from datetime import datetime, timedelta
import os
import random

import streamer.lib.youtube.stream as youtube
import streamer.lib.helper as helper
import streamer.lib.image.modifier as image

from airflow import DAG
from airflow import models
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker_operator import DockerOperator


# Ключевые настройки
DATA_DIR = './data'
INTERVAL = 60 # min
MIN_VIDEO_DURATION = 90 # какая минимальная длительность видео для стрима в секундах
CLIP_DURATION = 9

VIDEO_SOURCE_PATH = "video/masa_live_1920_1080"
VIDEO_PLAYLIST = "stream_list/videolist_disposable.txt"
AUDIO_PLAYLIST = "stream_list/audiolist_disposable.txt"

STREAM_TITLE = "СВОДКА НОВОСТЕЙ"
STREAM_DESCRIPTION = "Самые актуальные новости на данный момент"
#STREAM_THUMBNAIL_FILE = "youtube_streamer/masa_chronicle.png"

# настройки обложки
IMAGE_FONT = 'youtube_streamer/fonts/Geist-UltraBlack.otf'
IMAGE_FONT_SIZE = 80
#IMAGE_INPUT_PATH = 'youtube_streamer/images/masa_chronicle.png'
IMAGE_INPUT_PATH = ''
IMAGE_RESULT_DIR = 'images/'
TIMEZONE = 3

DAG_ID = "youtube_stream_dag"
#youtube
#KEY="jww0-gred-8vfj-tduk-fa13"
#URL="rtmp://a.rtmp.youtube.com/live2"
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
    result = []
    file_list = helper.get_files_list(video_dir, ['mp4'])
    # записываем в плейлист
    with open(playlist_path, 'w') as playlist_file:
        playlist_file.write('ffconcat version 1.0\n')
        # add intro
        #playlist_file.write('file \'intro.mp4\'\n')
        for file in file_list:
            #if file.endswith(".mp4"):  # adjust file extension as needed
            playlist_file.write(f"file '{video_dir}/{file}'\n")
            result.append(f"{video_dir}/{file}")
        #playlist_file.write("file 'videolist.txt'\n")
                
    return result


# переделать так что бы загружадась реальная длитильность клипа
@task.python
def calc_video_duration(file_list):
    clip_duration = CLIP_DURATION
    video_duration = clip_duration * len(file_list)
    #for file in file_list:
    #  video_duration += clip_duration

    if video_duration < MIN_VIDEO_DURATION:
        print("Small video")
        raise AirflowSkipException
    
    return video_duration

@task.python
def create_thumbnail():
    # Если указан IMAGE_INPUT_PATH применяем его иначе берем случайное изображение из директории с видеофрагментами
    if IMAGE_INPUT_PATH != '':
        image_input_path = IMAGE_INPUT_PATH 
    else:
        image_list = helper.get_files_list(VIDEO_SOURCE_PATH, ['png', 'jpeg', 'jpg'])
        if len(image_list) == 0:
            print("Empty thumbnail list")
            raise AirflowSkipException
        image_file = random.choice(image_list)
        image_input_path = f"'{VIDEO_SOURCE_PATH}/{image_file}'"
    
    image_out_path = IMAGE_RESULT_DIR + helper.generate_filename(image_input_path)
    # Пример использования функции
    text = helper.get_formated_time(format=None, round=False, timezone=TIMEZONE)
    if image.place_text_center(image_input_path, image_out_path, text, IMAGE_FONT, IMAGE_FONT_SIZE):
        return image_out_path
    return None

@task.python
def create_stream(thumbnail_file):
    ingestion = youtube.create_stream(STREAM_TITLE, STREAM_DESCRIPTION, thumbnail_file)
    if ingestion == None:
        print("Stream not created")
        raise AirflowSkipException
    return ingestion

@task.python
def run_ffmpeg_stream(rtmps_addr, video_playlist, audio_playlist, video_duration):
    ffmpeg_command = [
        "-re", "-f", "concat", "-safe", "0", "-i", video_playlist,
        "-re", "-f", "concat", "-i", audio_playlist,
        "-c:v", "copy", "-c:a", "copy",
        "-f", "flv", "-g", "60", "-t", str(video_duration),
        "-flvflags", "no_duration_filesize", rtmps_addr
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
    

with models.DAG(
    DAG_ID,
    schedule=timedelta(minutes=INTERVAL),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["polihoster", "streamer", "test"],
) as dag:
    
    create_playlist_task = create_video_playlist(VIDEO_SOURCE_PATH, VIDEO_PLAYLIST)
    video_duration_task = calc_video_duration(create_playlist_task)
    thumbnail_addr_task = create_thumbnail()
    #rtmps_addr_task = create_stream(thumbnail_addr_task)
    #ffmpeg_task = run_ffmpeg_stream(rtmps_addr_task, VIDEO_PLAYLIST, AUDIO_PLAYLIST, video_duration_task)
    #delete_files_task = delete_used_files(create_playlist_task)

    create_playlist_task >> video_duration_task
    video_duration_task >> thumbnail_addr_task
    #thumbnail_addr_task >> rtmps_addr_task
    #rtmps_addr_task >> ffmpeg_task
    #ffmpeg_task >> delete_files_task

    #cleanup_files_task >> 
    #create_playlist_task >> ffmpeg_stream_task >> cleanup_files_task
    #ffmpeg_stream_task