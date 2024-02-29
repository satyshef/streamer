import os
import subprocess
import json

# Генерирует плейлист m3u8 Нужно проверить корректность работы

def get_video_duration(file_path):
    # Получаем информацию о длительности видео с помощью ffprobe
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    else:
        print("Failed to get video duration.")
        return None

def segment_and_create_playlist(directory, output_playlist):
    # Поиск всех файлов MP4 в указанной директории
    mp4_files = [file for file in os.listdir(directory) if file.endswith('.mp4')]
    
    with open(output_playlist, 'w') as f_playlist:
        f_playlist.write('#EXTM3U\n')
        f_playlist.write('#EXT-X-VERSION:3\n')
        f_playlist.write('#EXT-X-TARGETDURATION:10\n')
        f_playlist.write('#EXT-X-MEDIA-SEQUENCE:0\n')
        
        # Создание общего плейлиста M3U8
        for index, mp4_file in enumerate(mp4_files):
            input_file = os.path.join(directory, mp4_file)
            output_base = os.path.splitext(mp4_file)[0]
            #output_base = 'segment'
            #file_name = f'{output_base}_{index:03d}.ts'
            # Получаем длительность видео
            duration = get_video_duration(input_file)
            if duration is None:
                continue
            
            # Создаем сегменты с учетом длительности видео
            segment_command = [
                'ffmpeg', '-i', input_file, '-c', 'copy',
                '-f', 'segment', '-segment_time', str(duration), '-segment_format', 'mpegts',
                f'{output_base}_%d.ts'
            ]
            subprocess.run(segment_command)

            # Добавляем сегменты в общий плейлист M3U8
            f_playlist.write(f'#EXTINF:{duration},\n')
            f_playlist.write(f'{output_base}_0.ts\n')
        
        # Добавляем окончание плейлиста
        f_playlist.write('#EXT-X-ENDLIST\n')

directory = './'
output_playlist = 'playlist.m3u8'

segment_and_create_playlist(directory, output_playlist)
