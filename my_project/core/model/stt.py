from typing import Callable
import json
import queue
import sys
import sounddevice as sd

import vosk

from core.config import setting


class STT:
    def __init__(self):
        self.__SAMPLERATE__ = setting.conf_stt.samplerate
        self.__REC__ = vosk.KaldiRecognizer(
            vosk.Model(str(setting.conf_stt.path_model)), self.__SAMPLERATE__
        )
        self.__Q__ = queue.Queue()

    def q_callback(self, indata, _, __, status):
        if status:
            print(status, file=sys.stderr)
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
            while True:
                data = self.__Q__.get()
                if self.__REC__.AcceptWaveform(data):
                    executor(json.loads(self.__REC__.Result())["text"])
