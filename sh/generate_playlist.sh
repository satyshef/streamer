#!/bin/bash
# Генератор списка видеофайлов для ffmpeg 
# Путь к директории с вашими видео файлами
directory_path="video"
FILE_NAME="videolist.txt"
# Создание или очистка файла playlist.txt
> $FILE_NAME

# Перечисление файлов в директории и запись их в playlist.txt
for file in "$directory_path"/*
do
    echo "file '$file'" >> $FILE_NAME
done