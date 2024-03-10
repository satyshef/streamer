import lib.youtube.stream as youtube
import lib.helper as helper
import lib.image.modifier as image

TITLE = "СВОДКА НОВОСТЕЙ"
DESCRIPTION = "Самые актуальные новости на данный момент"
THUMBNAIL_FILE = "youtube_streamer/masa_stream.png"

def test_youtube_stream():
    ingestion = youtube.create_stream(TITLE, DESCRIPTION, THUMBNAIL_FILE, "public")
    print(ingestion)

def test_text_image():
    IMAGE_FONT = 'youtube_streamer/fonts/Geist-UltraBlack.otf'
    IMAGE_FONT_SIZE = 80
    IMAGE_INPUT_PATH = 'youtube_streamer/images/masa_stream.png'
    IMAGE_RESULT_DIR = 'result/'
    TIMEZONE = 3
   
    image_out_path = IMAGE_RESULT_DIR + helper.generate_filename(IMAGE_INPUT_PATH)
    # Пример использования функции
    text = helper.get_news_time(format=None, round=False, timezone=TIMEZONE)
    if image.place_text_center(IMAGE_INPUT_PATH, image_out_path, text, IMAGE_FONT, IMAGE_FONT_SIZE):
        return image_out_path
    return None

if __name__ == '__main__':
    img_path = test_text_image()
    print(img_path)
    
    
   