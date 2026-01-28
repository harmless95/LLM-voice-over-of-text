import re, socket
import asyncio
import threading

from fuzzywuzzy import fuzz
from core.config import setting
from core.model import tts, stt, translate_text
from utils.translate_text import main_message

FLAG_STT = False

token = setting.conf_tw.token
username = setting.conf_tw.username
channel = setting.conf_tw.channel

sock = socket.socket()
sock.connect(("irc.chat.twitch.tv", 6667))
sock.send(f"PASS oauth:{token}\n".encode())
sock.send(f"NICK {username}\n".encode())
sock.send(f"JOIN #{channel}\n".encode())


def clean_text(text):
    return re.sub(r"[^\w\s!?.,]", "", text)


def extract_message(raw_response):
    match = re.search(
        r":(\w+)!\w+@[\w\.]+\.tmi\.twitch\.tv PRIVMSG #[\w-]+ :(.+)", raw_response
    )
    if match:
        username, message = match.groups()
        return [username, message]  # "harmless95 проверка"
    return None


# [val for key, val in dict.items() if text.lower() in key]
def equ(text, needed):
    return fuzz.ratio(text, needed) >= 70


def execute(text: str):
    if not text.strip():  # Игнорируем тишину на входе
        return

    global FLAG_STT
    command_start = "Бобр старт"
    command_stop = "Бобр стоп"

    if equ(text=text, needed=command_start):
        FLAG_STT = True
        print("Start Бобр")
        tts.text2speech(text="Режим бобра включен", lang=0)
        return

    elif equ(text=text, needed=command_stop):
        FLAG_STT = False
        stt.active = False
        print("Stop Бобр")
        tts.text2speech(text="Режим бобра отключён", lang=0)
        return

    if FLAG_STT and text != "":
        print(f"Распознано: {text}")
        en_text = translate_text(text_ru=text)
        result_text_en = en_text[0].get("translation_text")
        tts.text2speech(text=result_text_en, lang=1)


def main():
    def stt_thread():
        """STT в отдельном потоке"""
        stt.listen(execute)

    # ✅ STT в фоне
    stt_daemon = threading.Thread(target=stt_thread, daemon=True)
    stt_daemon.start()
    print("🎙️ STT запущен в фоне")
    while True:
        response = sock.recv(4096).decode("utf-8")
        if response.startswith("PING"):
            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            message = extract_message(response)
            if message:
                clean_message = main_message(text=message)
                print(f"Message:{clean_message}")
                tts.text2speech(clean_message, lang=0)


if __name__ == "__main__":
    main()
