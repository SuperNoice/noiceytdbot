#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.


import logging
import os
import re
import shutil
import time
import traceback
import sys
import json

from telegram import ForceReply, Update, Message, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import *

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from colored import fg, attr
f_colored = fg(117)
r = fg(1)
b = attr(0)
import fontstyle as fs
import yt_dlp


def load_threads_priority():
    if not os.path.exists("./threads_priority.json"):
        return {}
    
    with open("./threads_priority.json", "r") as file:
        content = file.read()
        if content == "": return {}
        try:
            return json.loads(content)
        except:
            return {}
    

def write_threads_priority(dict):
    with open("./threads_priority.json", "w") as file:
        file.write(json.dumps(dict))


yt_url_pattern = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/((.+\s)|(.+$))")
yt_clearing_url_pattern = re.compile(r"&.+")
yt_vid_id_pattern = re.compile(r"(^https?://)?(www\.)?(youtube\.com|youtu\.be)/((clip/)|(shorts/)|(watch\?v=))?|\?.+|\?$|&.+")

threads_priority = load_threads_priority()


class StatusMessage:

    message: Message
    status: str
    last_timestamp = 0
    status_update_rate = 3

    def __init__(self, message: Message):
        self.message = message
        self.status = message.text
    
    async def change_status(self, new_status: str):
        self.status = new_status
        await self.message.edit_text(new_status)

    async def delete(self):
        await self.message.delete()


def sanitize_title(name) -> str:
    return re.sub(r'(\s+)?#\w+', "", name).rstrip(' -')


def getVidId(url):
    return yt_vid_id_pattern.sub("", url)


def clearVidFolder():
    folder = "./videos"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


async def dl_mp4(url, destination, status_message: StatusMessage):
    url = yt_clearing_url_pattern.sub("", url)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "cookiefile": "cookies.txt",
        "js_runtimes": {'deno': {'path': R'../node_modules/deno'}},
        "remote_components": ["ejs:github"],
    }

    await status_message.change_status("Статус: Получение информации о видео")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            ydl.close()
    except yt_dlp.utils.DownloadError as e:
        print(fs.apply(f"An error occurred: {e}", "/red/bold"))
        raise e

    print(fs.apply(f"\nStarting Video Download...\n", "/cyan/bold"))
    time1 = int(time.time())
    vid_title = sanitize_title(info["title"])
    if vid_title == "": vid_title = "Без названия"
    vid_path = os.path.join(destination, getVidId(url) + ".mp4")

    ydl_opts = {
        "outtmpl": vid_path,
        'format': "bestvideo[ext=mp4][height<=1280]+bestaudio[ext=m4a]/mp4",
        "cookiefile": "cookies.txt",
        "js_runtimes": {'deno': {'path': R'../node_modules/deno'}},
        "remote_components": ["ejs:github"],
    }

    await status_message.change_status("Статус: Скачивание видео")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            def progress_hook(info):
                if (info["total_bytes"] / (1024 ** 3)) > 1.7:
                    raise Exception("Error: Файл слишком большой")

            ydl.add_progress_hook(progress_hook)
            ydl.download([url])
            print(
                fs.apply(
                    "Video has been successfully downloaded.",
                    "/green/bold",
                )
            )
            ydl.close()
    except Exception as e:
        print(
            fs.apply(f"Failed to download '{vid_title}': {e}", "/red")
        )
        raise e

    time2 = int(time.time())
    ftime = time2 - time1
    print(
        "\n" + fs.apply("Time taken to download:", "/cyan/bold"),
        fs.apply(f"{ftime} sec", "/cyan"),
    )

    return vid_title, vid_path



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

err_array = ["no errors"]

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def process_yt_link_message(message_with_url: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    if message_with_url is not None:
        try:
            video_url = yt_url_pattern.search(message_with_url.text)
            if video_url is None: return
            video_url = video_url[0].strip(" ")
            message = ("\n" + yt_url_pattern.sub(" ", message_with_url.text)).rstrip("\n ")

            chat_id = message_with_url.chat_id
            message_thread_id = threads_priority.get(chat_id)
            if message_thread_id is None:
                message_thread_id = message_with_url.message_thread_id

            await message_with_url.set_reaction("👀")
            status_message = StatusMessage(await context.bot.send_message(chat_id, "Статус: Запуск", message_thread_id=message_thread_id, disable_notification=True))
            
            vid_title, file_path = await dl_mp4(video_url, R"./videos", status_message)
        
            await status_message.change_status("Статус: Отправка видео")

            if (os.path.getsize(file_path) / (1024 ** 3)) > 2:
                    raise Exception("Error: Файл слишком большой")
            
            await context.bot.send_video(
                chat_id, 
                file_path, 
                supports_streaming=True, 
                write_timeout=180,
                pool_timeout=180,
                read_timeout=180,
                connect_timeout=180,
                caption=f"<a href=\"{video_url}\">{vid_title}</a>{message}<i>\nby {message_with_url.from_user.name}</i>",
                parse_mode="HTML",
                reply_to_message_id=message_with_url.reply_to_message.id if message_with_url.reply_to_message is not None else None,
                message_thread_id=message_thread_id
            )

            await message_with_url.delete()
            await status_message.delete()

        except Exception as e:
            await message_with_url.set_reaction("👎")
            await status_message.change_status(status_message.status.replace("Статус:", "Ошибка на этапе:"))
            await message_with_url.reply_text(str(e).split("\n")[-1].replace("[0;31m", "").replace("[0m", ""))

            exception = traceback.format_exc()
            err_array.append(exception[:min(4000, len(exception))//2] + exception[-(min(4000, len(exception))//2):])
            if len(err_array) > 5 or err_array[0] == "no errors":
                err_array.remove(err_array[0])
        
        clearVidFolder()

        return


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await process_yt_link_message(update.message, context)
    return


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message is None:
        await update.message.reply_text("Используйте эту команду в ответе на сообщение, которое требуется скачать")
    else:
        await process_yt_link_message(update.message.reply_to_message, context)
        await update.message.delete()
    return


async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        for err in err_array:
            await update.effective_user.send_message(err, message_thread_id=update.message.message_thread_id)
    except Exception as e:
        await update.message.reply_text(str(e))


async def set_default_thread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global threads_priority
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id

    if thread_id is None:
        await update.message.reply_text(f"В этом чате нет топиков", message_thread_id=thread_id)
    else:
        threads_priority[chat_id] = thread_id
        write_threads_priority(threads_priority)
        await update.message.reply_text(f"Теперь видео будут отправлятся в этот топик", message_thread_id=thread_id)


def main() -> None:
    if not os.path.exists("./videos"):
        os.mkdir("./videos")

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().base_url("http://localhost:8081/bot").token(f"{os.getenv("BOT_TOKEN")}").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("download", download))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("default", set_default_thread))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
