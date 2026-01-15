import re, socket
import asyncio
import threading

from fuzzywuzzy import fuzz

from core.config import setting
from core.model import tts
from core.model import stt


token = setting.conf_tw.token
username = setting.conf_tw.username
channel = setting.conf_tw.channel

sock = socket.socket()
sock.connect(("irc.chat.twitch.tv", 6667))
sock.send(f"PASS oauth:{token}\n".encode())
sock.send(f"NICK {username}\n".encode())
sock.send(f"JOIN #{channel}\n".encode())


dict_name = {
    "harmless95": "Хармлесс 95",
    "UmoPsychoDior": "Умо Психо Диор",
    "VadimVK777": "Вадим ВК 777",
}


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
    print(f"> {text}")
    text_bobr = "бобр отправь сообщение"

    if equ(text, "расскажи анектдот"):
        text = "какой то анекдот!"
        tts.text2speech(text)
        print(f"- {text}")

    elif equ(text, "что ты умеешь"):
        text = "я умею всё, чему ты мен+я науч+ил!"
        tts.text2speech(text)
        print(f"- {text}")

    elif equ(text, "выключи"):
        text = "надеюсь, я не стану про+ектом, кот+орый ты забр+осишь!"
        tts.text2speech(text)
        print(f"- {text}")
        raise SystemExit
    if text_bobr in text:
        equ(text, "бобр отправь сообщение")
        result_text = text.lower().split(text_bobr)
        text = f"Я не бобр, но сообщение {result_text[1:]} было отправлено!"
        tts.text2speech(text)
        print(f"- {text}")


def main():
    # def stt_thread():
    #     """STT в отдельном потоке"""
    #     stt.listen(execute)

    # ✅ STT в фоне
    # stt_daemon = threading.Thread(target=stt_thread, daemon=True)
    # stt_daemon.start()
    print("🎙️ STT запущен в фоне")
    while True:
        response = sock.recv(4096).decode("utf-8")
        if response.startswith("PING"):
            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            print("--", response)  # Здесь можно обрабатывать сообщения
            message = extract_message(response)
            if message:
                clean_message = clean_text(message[1])
                name = [
                    vol for key, vol in dict_name.items() if key.lower() == message[0]
                ]
                if not name:
                    name = "новый пользователь"
                print(f"Message:{name} {clean_message}")
                message_sound = f"{name} {clean_message}"
                tts.text2speech(message_sound)


if __name__ == "__main__":
    main()
