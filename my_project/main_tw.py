import queue
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
import re
import socket
import threading

from core.config import setting, logger
from core.constants import Twitch_HOST, Twitch_PORT, TTS_DEFAULT_LANG
from core.model import tts, stt, Commands
from utils.translate_text import main_message

voice_queue = queue.Queue()

token = setting.conf_tw.token
username = setting.conf_tw.username
channel = setting.conf_tw.channel
last_user = ""

com_all = Commands(voice_queue=voice_queue)


class TwitchChatClient:
    def __init__(self, token: str, username: str, channel: str):
        self._token = token
        self._username = username
        self._channel = channel
        self._sock: socket.socket | None = None

    @property
    def sock(self) -> socket.socket | None:
        return self._sock

    def connect(self) -> None:
        """
        Подключение к чату твича с автоматическим ретраем.
        """
        while True:
            try:
                sock = socket.socket()
                sock.connect((Twitch_HOST, Twitch_PORT))
                sock.send(f"PASS oauth:{self._token}\r\n".encode())
                sock.send(f"NICK {self._username}\r\n".encode())
                sock.send(f"JOIN #{self._channel}\r\n".encode())
                self._sock = sock
                logger.info("Успешно подключено к Twitch IRC как %s", self._username)
                return
            except Exception as e:
                logger.error(
                    "Не удалось подключиться к Twitch IRC: %s. Пробую снова через 5 сек...",
                    e,
                )
                time.sleep(5)

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except Exception:
                pass
            finally:
                self._sock = None

    def send_pong(self) -> None:
        if self._sock is None:
            return
        try:
            self._sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        except Exception as e:
            logger.error("Не удалось отправить PONG: %s", e)

    def iter_lines(self, timeout: float = 5.0):
        """
        Бесконечный генератор пакетов строк из Twitch IRC
        с автоматическим переподключением.
        """
        if self._sock is None:
            self.connect()

        while True:
            try:
                assert self._sock is not None
                self._sock.settimeout(timeout)
                response = self._sock.recv(4096).decode("utf-8", errors="ignore")
                if not response:
                    logger.error("Пустой ответ от Twitch IRC")
                    raise socket.error("Empty response")
                logger.info("Response: %s", response)
                yield response.split("\r\n")
            except socket.timeout:
                # Просто продолжаем ждать новые сообщения
                continue
            except (ConnectionError, socket.error, UnicodeDecodeError) as e:
                logger.error(
                    "Соединение разорвано (%s). Переподключение через 5 сек...", e
                )
                self.close()
                time.sleep(5)
                self.connect()


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


def handler_lines(lines, send_pong):
    for line in lines:
        if not line:
            continue

        if line.startswith("PING"):
            send_pong()
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
        voice_queue.put((clean_message, TTS_DEFAULT_LANG))


def stt_thread():
    """STT в отдельном потоке"""
    stt.listen(com_all.execute)


def main():
    client = TwitchChatClient(token=token, username=username, channel=channel)

    # TTS
    tts_voice = threading.Thread(target=voice_worker, daemon=True, name="TTS-Worker")
    # STT
    stt_daemon = threading.Thread(target=stt_thread, daemon=True, name="STT-Worker")

    tts_voice.start()
    stt_daemon.start()
    logger.info("🎙️ STT запущен в фоне")
    try:
        for lines in client.iter_lines():
            if not tts_voice.is_alive():
                logger.error(
                    "КРИТИЧЕСКАЯ ОШИБКА: Поток озвучки (TTS) упал! Перезапуск..."
                )
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

            handler_lines(lines=lines, send_pong=client.send_pong)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки, завершаю работу...")
    finally:
        client.close()
        # Останавливаем STT и воркер озвучки
        stt.stop()
        voice_queue.put(None)
        # Даём потокам время корректно завершиться
        tts_voice.join(timeout=5)
        stt_daemon.join(timeout=5)


if __name__ == "__main__":
    main()
