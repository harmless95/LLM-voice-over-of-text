import asyncio
import re

from fuzzywuzzy import fuzz

from core.model import stt, tts
from main_tw import sock


def clean_text(text):
    return re.sub(r"[^\w\s!?.,]", "", text)[:100]


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


def extract_message(raw_response):
    match = re.search(r"PRIVMSG #[\w-]+ :(.+)", raw_response)
    if match:
        return match.group(1)
    return None


def start_tts():
    while True:
        response = sock.recv(2048).decode("utf-8")
        if response.startswith("PING"):
            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            print(response)  # Здесь можно обрабатывать сообщения
            message = extract_message(response)
            if message:
                clean_message = clean_text(message)
                print(f"Message: {clean_message}")
                tts.text2speech(clean_message)


def start_stt():
    stt.listen(execute)
    print("🎙️ STT запущен в фоне")


async def main():
    run_tts = asyncio.to_thread(start_tts())
    run_stt = asyncio.to_thread(start_stt())
    starting = await asyncio.gather(run_stt, run_tts)


if __name__ == "__main__":
    asyncio.run(main())
