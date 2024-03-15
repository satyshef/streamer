import lib.youtube.stream as youtube
import lib.helper as helper
import lib.image.modifier as image


def test_youtube_stream():
    TITLE = "СВОДКА НОВОСТЕЙ"
    DESCRIPTION = "Самые актуальные новости на данный момент"
    THUMBNAIL_FILE = "youtube_streamer/images/masa_stream.png"
    ingestion = youtube.create_stream(TITLE, DESCRIPTION, THUMBNAIL_FILE, "public")
    print(ingestion)

def test_text_image():
    IMAGE_FONT = 'youtube_streamer/fonts/Geist-UltraBlack.otf'
    IMAGE_FONT_SIZE = 70
    IMAGE_INPUT_PATH = 'youtube_streamer/images/masa_chronicle.png'
    IMAGE_RESULT_DIR = 'result/'
    TIMEZONE = 3
   
    image_out_path = IMAGE_RESULT_DIR + helper.generate_filename(IMAGE_INPUT_PATH)
    # Пример использования функции
    text = helper.get_formated_time(format=None, round=False, timezone=TIMEZONE)
    if image.place_text(input_path=IMAGE_INPUT_PATH, output_path=image_out_path, text=text, x_pos=0, y_pos=-300, font_path=IMAGE_FONT, font_size=IMAGE_FONT_SIZE):
        return image_out_path
    return None

if __name__ == '__main__':
    #lst = helper.get_files_list('/Users/outsider/Downloads/newsvideo/export', ['mp4'])
    test_youtube_stream()
    #img_path = test_text_image()
    #print(lst)
    
    
   