import re
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
        put_accent: bool = setting.conf_tts.put_accent,
        put_yo: bool = setting.conf_tts.put_yo,
        put_stress_homo: bool = setting.conf_tts.put_stress_homo,
        put_yo_homo: bool = setting.conf_tts.put_yo_homo,
    ):
        self.__MODEL__, _ = LOADING_MODEL
        self.__MODEL__.to(torch.device(device))

        self.__SPEAKER__ = speaker
        self.__SAMPLERATE__ = samplerate
        self.__PUT_ACCENT__ = put_accent
        self.__PUT_YO__ = put_yo
        self.__PUT_STRESS_HOMO__ = put_stress_homo
        self.__PUT_YO_HOMO__ = put_yo_homo

    def should_speak(self, text: str) -> bool:
        text = text.strip()
        if (
            len(text) < 2
            or text.isdigit()
            or re.match(r"^\W+$", text)
            or len(text.split()) == 1
            and text.lower() in ["test", "тест", "кек"]
        ):
            return False
        return True

    def text2speech(self, text: str):

        if not self.should_speak(text):
            print(f"⏭️ Skip: '{text}'")
            return

        try:
            print(f"🎙️ Говорит: '{text}'")
            audio = self.__MODEL__.apply_tts(
                text=text,
                speaker=self.__SPEAKER__,
                sample_rate=self.__SAMPLERATE__,
                put_accent=self.__PUT_ACCENT__,
                put_yo=self.__PUT_YO__,
                put_stress_homo=self.__PUT_STRESS_HOMO__,
                put_yo_homo=self.__PUT_YO_HOMO__,
            )
            sd.play(audio, samplerate=self.__SAMPLERATE__)
            sd.wait()  # ✅ Идеально!
        except Exception as e:
            print(f"⚠️ TTS fail: {e}")


tts = TTS()
