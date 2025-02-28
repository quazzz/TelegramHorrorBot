# imports
from os import getenv
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import telebot
# variables
video_idx = 0
cur_id = ''
# constants
HTTP_TOKEN = getenv("TELEGRAM_HTTP_TOKEN")
if not HTTP_TOKEN:
    raise ValueError('Нету токена.')
VIDEOS_PATH = './videos'
DOWNLOAD_PATH = './download'
# init bot 
bot = telebot.TeleBot(HTTP_TOKEN)
# main keyboard

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Выбрать видео'))
    keyboard.add(KeyboardButton('Помощь'))
    return keyboard
# video keyboard

def video_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(2):
        keyboard.add(KeyboardButton(str(i+1)))
    return keyboard
# start handler

@bot.message_handler(commands=['start','help'])
def send_welcome_msg(message):
    bot.send_message(
        message.chat.id,
        'Привет, выбери видео для кружка и скинь мне его потом ;)',
        reply_markup=main_keyboard()
    )
# choosing video
@bot.message_handler(func=lambda message: message.text == 'Выбрать видео')
def choose_video(message):
    bot.send_message(
        message.chat.id, 
        'Выбери видео для кружка', 
        reply_markup=video_keyboard()
        )
# choosing the video via number entering
@bot.message_handler(func=lambda message: message.text in ['1', '2'])
def video_chosen(message):
    global video_idx
    video_idx = int(message.text)
    bot.send_message(
        message.chat.id,
        f'Отлично! Видео номер {video_idx} Теперь отправь мне видео, которое ты хочешь использовать для кружка.'
    )
# help handler
@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_message(message):
    bot.send_message(
        message.chat.id,
        "Выбери видео и скинь кружок, я сделаю хоррор кружок!"
        )
# getting video note 
@bot.message_handler(content_types=['video_note'])
def handle_video(message):
    # if user didn't select video then ask him to do it
    if video_idx <= 0:
        bot.send_message(message.chat.id, 'Выбери сначала видео, пожалуйста')
        return  

    # getting the video note
    video_note = message.video_note
    # and the note id
    file_id = video_note.file_id
    # debugging 
    print(f"Получен file_id: {file_id}") 
    # bot gets file
    video_file = bot.get_file(file_id)
    if not video_file:
        bot.send_message(message.chat.id, 'Не удалось получить файл.')
        return
    # getting path
    file_path = video_file.file_path
    print(f"Получен путь файла: {file_path}")  

     # downloading the file
    downloaded_file = bot.download_file(file_path)
    if not downloaded_file:
        bot.send_message(message.chat.id, 'Не удалось скачать файл.')
        return
    # getting current file id
    global cur_id
    cur_id = file_id
    # getting the path for downloading the note
    save_path = os.path.join(DOWNLOAD_PATH, f'{file_id}.mp4')
    # downloading the note
    try:
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        print(f"Файл сохранён по пути: {save_path}") 

        bot.send_message(
            message.chat.id,
            'Кружок получен! Подождите пару секунд.',
            reply_markup=main_keyboard()
        )
        merge_video_and_send(file_id,message.chat.id)
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")  
        bot.send_message(message.chat.id, 'Произошла ошибка при сохранении файла.')
def merge_video_and_send(id, chat_id):
    # getting videos for concatenating
    video = f'./download/{id}.mp4'
    horror_video = f'./videos/{video_idx}.mp4'
    
    # load video clips
    video_clip = VideoFileClip(video)
    horror_video_clip = VideoFileClip(horror_video)
    
    # set both to the same resolution 
    target_resolution = (video_clip.size[0], video_clip.size[1])
    horror_video_clip = horror_video_clip.resize(target_resolution)
    
    # set the same frame rate for both videos
    frame_rate = video_clip.fps
    horror_video_clip = horror_video_clip.set_fps(frame_rate)
    
    # concatenate clips
    loaded = [video_clip, horror_video_clip]
    final_clip = concatenate_videoclips(loaded)
    
    # output final video
    output_path = 'video.mp4'
    final_clip.write_videofile(output_path)
    final_clip.close()  
    
    # send the video
    with open(output_path, 'rb') as video_file:
        bot.send_video_note(chat_id, video_file)
# starting the bot
bot.polling()


