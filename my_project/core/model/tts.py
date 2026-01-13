import time

import torch
import sounddevice as sd

from core.config import setting
from core.model.load_model import LOADING_MODEL


class TTS:
    def __init__(
        self,
        speaker: str = setting.conf_tts.SPEAKER,
        device: str = setting.conf_tts.DEVICE,
        samplerate: int = setting.conf_tts.samplerate,
    ):
        self.__MODEL__, _ = LOADING_MODEL
        self.__MODEL__.to(torch.device(device))

        self.__SPEAKER__ = speaker
        self.__SAMPLERATE__ = samplerate

    def text2speech(self, text: str):
        audio = self.__MODEL__.apply_tts(
            text=text,
            speaker=self.__SPEAKER__,
            sample_rate=self.__SAMPLERATE__,
            put_accent=True,
            put_yo=True,
        )

        sd.play(audio, samplerate=self.__SAMPLERATE__)
        time.sleep((len(audio) / self.__SAMPLERATE__))
        sd.stop()
