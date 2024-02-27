#!/bin/bash

# Путь к директории с вашими видео файлами
directory_path="/root/apps/text2video/out/masa_live_1920_1080"
#directory_path="video/masa_live_1920_1080"
#directory_path="video/masa_live"

# Создание или очистка файла playlist.txt
> playlist.txt

# Перечисление файлов в директории и запись их в playlist.txt
for file in "$directory_path"/*
do
    echo "file '$file'" >> playlist.txt
done