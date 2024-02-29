# Генерирует плейлист m3u8 Нужно проверить корректность работы
ffmpeg -f concat -safe 0 -i <(for f in ./*.mp4; do echo "file '$PWD/$f'"; done) -c copy playlist.m3u8

