import lib.youtube.stream as youtube

TITLE = "СВОДКА НОВОСТЕЙ"
DESCRIPTION = "Самые актуальные новости на данный момент"
THUMBNAIL_FILE = "youtube_streamer/masa_stream.png"

if __name__ == '__main__':
    ingestion = youtube.create_stream(TITLE, DESCRIPTION, THUMBNAIL_FILE, "public")
    print(ingestion)
    
   