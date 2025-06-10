import telebot
import yt_dlp
import os
import glob
import traceback

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def send_track(message):
    query = message.text.strip()

    # Видаляємо старі тимчасові файли
    try:
        for f in glob.glob("temp_audio*"):
            os.remove(f)
    except Exception as cleanup_error:
        print(f"Не вдалося видалити файл: {f} - {cleanup_error}")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1'
    }

    bot.send_message(message.chat.id, f"Шукаю: {query} 🎵", parse_mode="Markdown")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(query, download=True)
            title = info_dict.get('title', query)
    except Exception as e:
        error_text = traceback.format_exc()
        bot.send_message(message.chat.id, f"❌ Помилка при завантаженні:\n```\n{error_text}\n```", parse_mode="Markdown")
        return

    if os.path.exists("temp_audio.mp3"):
        with open("temp_audio.mp3", "rb") as audio:
            bot.send_audio(message.chat.id, audio, title=title)
        os.remove("temp_audio.mp3")
    else:
        bot.send_message(message.chat.id, "❌ Файл temp_audio.mp3 не знайдено. Можливо, не вдалося завантажити трек.")

bot.polling(none_stop=True)