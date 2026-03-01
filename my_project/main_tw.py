import queue
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
import re, socket
import threading

from core.config import setting, logger
from core.model import tts, stt, Commands
from utils.translate_text import main_message

voice_queue = queue.Queue()

token = setting.conf_tw.token
username = setting.conf_tw.username
channel = setting.conf_tw.channel
last_user = ""

com_all = Commands(voice_queue=voice_queue)


def extract_message(raw_response):
    global last_user
    match = re.search(
        r":(\w+)!\w+@[\w\.]+\.tmi\.twitch\.tv PRIVMSG #[\w-]+ :(.+)",
        raw_response,
    )
    if match:
        username, message = match.groups()
        if last_user.lower() == username.lower():
            return ["", message]
        last_user = username
        return [username, message]  # "harmless95 проверка"
    return None


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
            logger.error("Не удалось подключиться: %s. Пробую снова через 5 сек...", e)
            time.sleep(5)


def voice_worker():
    """
    Получаем сообщение из очереди и озвучивает
    """
    while True:
        logger.info("Receiving from Queue")
        try:
            item = voice_queue.get()
            if item is None:
                break
            text, lang = item
            if text:
                try:
                    logger.info("Message for TTS: %s", text)
                    tts.text2speech(text=text, lang=lang)
                    logger.info("Completed TTS")
                except Exception as e:
                    logger.error("Ошибка TTS: %s", e)
        except Exception as e:
            logger.critical("Непредвиденная ошибка в воркере: %s", e, exc_info=True)
            time.sleep(1)  # Пауза, чтобы не спамить в лог при циклической ошибке
        finally:
            voice_queue.task_done()


def handler_lines(lines, sock):
    for line in lines:
        if not line:
            continue

        if line.startswith("PING"):
            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            continue

        logger.info("Receiving the user and his message: %s", line)
        message = extract_message(line)
        if not message:
            continue

        logger.info("Message before processing: %s", message)
        clean_message = main_message(text=message)
        if not clean_message:
            continue

        logger.info("The message was processed successfully")
        voice_queue.put((clean_message, "ru"))


def stt_thread():
    """STT в отдельном потоке"""
    stt.listen(com_all.execute)


def main():
    sock = sock_connection()

    # TTS
    tts_voice = threading.Thread(target=voice_worker, daemon=True, name="TTS-Worker")
    # STT
    stt_daemon = threading.Thread(target=stt_thread, daemon=True, name="STT-Worker")

    tts_voice.start()
    stt_daemon.start()
    logger.info("🎙️ STT запущен в фоне")

    logger.info("🎙️ STT запущен в фоне")
    while True:
        if not tts_voice.is_alive():
            logger.error("КРИТИЧЕСКАЯ ОШИБКА: Поток озвучки (TTS) упал! Перезапуск...")
            tts_voice = threading.Thread(
                target=voice_worker, daemon=True, name="TTS-Worker"
            )
            tts_voice.start()
        if not stt_daemon.is_alive():
            logger.error(
                "КРИТИЧЕСКАЯ ОШИБКА: Поток распознавания (STT) упал! Перезапуск..."
            )
            stt_daemon = threading.Thread(
                target=stt_thread, daemon=True, name="STT-Worker"
            )
            stt_daemon.start()

        try:
            sock.settimeout(5.0)
            response = sock.recv(4096).decode("utf-8", errors="ignore")
            if not response:
                logger.error("Empty response", response)
                raise socket.error("Empty response")
            logger.info("Response: %s", response)
            lines = response.split("\r\n")
            handler_lines(lines=lines, sock=sock)

        except socket.timeout:
            continue

        except (ConnectionError, socket.error, UnicodeDecodeError) as e:
            logger.error("Соединение разорвано (%s). Переподключение через 5 сек...", e)
            try:
                sock.close()
            except:
                pass
            time.sleep(5)
            sock = sock_connection()


if __name__ == "__main__":
    main()
