import queue
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import re, socket
import asyncio
import threading


from fuzzywuzzy import fuzz
from core.config import setting
from core.model import tts, stt, translate_text
from utils.translate_text import main_message


FLAG_STT = False
voice_queue = queue.Queue()

token = setting.conf_tw.token
username = setting.conf_tw.username
channel = setting.conf_tw.channel


def extract_message(raw_response):
    match = re.search(
        r":(\w+)!\w+@[\w\.]+\.tmi\.twitch\.tv PRIVMSG #[\w-]+ :(.+)", raw_response
    )
    if match:
        username, message = match.groups()
        return [username, message]  # "harmless95 проверка"
    return None


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

def sock_connection():
    """
    Подключение к чату твича
    :return: sock - Соединение
    """
    while True:
        try:
            sock = socket.socket()
            sock.connect(("irc.chat.twitch.tv", 6667))
            sock.send(f"PASS oauth:{token}\r\n".encode())
            sock.send(f"NICK {username}\r\n".encode())
            sock.send(f"JOIN #{channel}\r\n".encode())
            return sock
        except Exception as e:
            print(f"❌ Не удалось подключиться: {e}. Пробую снова через 5 сек...")
            time.sleep(5)

def voice_worker():
    """
    Получаем сообщение из очереди и озвучивает
    """
    while True:
        item = voice_queue.get()
        if item is None:
            break
        text, lang = item
        if text:
            try:
                tts.text2speech(text=text, lang=lang)
            except Exception as e:
                print(f"Ошибка TTS: {e}")
        voice_queue.task_done()


def main():
    sock = sock_connection()
    threading.Thread(target=voice_worker, daemon=True).start()
    def stt_thread():
        """STT в отдельном потоке"""
        stt.listen(execute)

    # ✅ STT в фоне
    stt_daemon = threading.Thread(target=stt_thread, daemon=True)
    stt_daemon.start()
    print("🎙️ STT запущен в фоне")
    while True:
        try:
            response = sock.recv(4096).decode("utf-8")
            if not response:
                print("⚠️ Получена пустая строка. Переподключение...")
                raise socket.error("Empty response")

            lines = response.split("\r\n")
            for line in lines:
                if not line:
                    continue

                if line.startswith("PING"):
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

                else:
                    message = extract_message(line)
                    if message:
                        clean_message = main_message(text=message)
                        print(f"Message:{clean_message}")

                        voice_queue.put((clean_message, 0))

        except (ConnectionAbortedError, ConnectionResetError, socket.error, UnicodeDecodeError) as e:
            print(f"❌ Соединение разорвано ({e}). Переподключение через 5 сек...")
            try:
                sock.close()
            except:
                pass
            time.sleep(5)
            sock = sock_connection()



if __name__ == "__main__":
    main()
