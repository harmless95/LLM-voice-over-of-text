from typing import Callable
import json
import queue
import sys
import sounddevice as sd

import vosk

from core.config import setting, logger


class STT:
    def __init__(self):
        self.__SAMPLERATE__ = setting.conf_stt.samplerate
        self.__REC__ = vosk.KaldiRecognizer(
            vosk.Model(str(setting.conf_stt.path_model)), self.__SAMPLERATE__
        )
        self.__Q__ = queue.Queue()
        self.active = True

    def q_callback(self, indata, _, __, status):
        if status:
            logger.info("Status: %s, File: %s", status, file=sys.stderr)
        self.__Q__.put(bytes(indata))

    def listen(self, executor: Callable[[str], None]) -> None:
        with sd.RawInputStream(
            samplerate=self.__SAMPLERATE__,
            blocksize=setting.conf_stt.blocksize,
            device=setting.conf_stt.device,
            dtype=setting.conf_stt.dtype,
            channels=setting.conf_stt.channels,
            callback=self.q_callback,
        ):
            logger.info("Start listen")
            while self.active:
                data = self.__Q__.get()
                if not self.active:
                    break
                if self.__REC__.AcceptWaveform(data):
                    res = json.loads(self.__REC__.Result())["text"]
                    if res.strip():  # Вызываем только если текст не пустой
                        logger.info("Text STT: %s", res)
                        executor(res)

    def stop(self) -> None:
        """
        Останавливает цикл прослушивания и разблокирует очередь.
        """
        self.active = False
        # Кладём пустой блок, чтобы разблокировать .get() в listen
        try:
            self.__Q__.put_nowait(b"")
        except Exception:
            pass


stt = STT()
