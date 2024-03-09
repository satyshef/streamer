import libs.youtube.stream as youtube

TITLE = "СВОДКА НОВОСТЕЙ"
DESCRIPTION = "Самые актуальные новости на данный момент"
THUMBNAIL_FILE = "data/masa_stream.png"

if __name__ == '__main__':
    ingestion = youtube.create_stream(TITLE, DESCRIPTION, THUMBNAIL_FILE)
    print(ingestion)
    
   