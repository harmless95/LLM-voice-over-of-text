import re
import time

import torch
import sounddevice as sd

from core.config import setting
from core.model.load_model import LOADING_MODEL
from core.model.load_model_en import LOADING_MODEL_EN


class TTS:

    def __init__(
        self,
        speaker: str,
        speaker_en: str,
        device: str,
        samplerate: int,
        put_accent: bool,
        put_yo: bool,
        put_stress_homo: bool,
        put_yo_homo: bool,
    ):
        self.__MODEL__, _ = LOADING_MODEL
        self.__MODEL__.to(torch.device(device))

        self.__MODEL_EN__, _ = LOADING_MODEL_EN
        self.__MODEL_EN__.to(torch.device(device))

        self.__SPEAKER__ = speaker
        self.__SPEAKER_EN__ = speaker_en
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

    def text2speech(self, text: str, lang=0):

        if not self.should_speak(text):
            print(f"⏭️ Skip: '{text}'")
            return

        try:
            print(f"🎙️ Говорит: '{text}'")
            if lang == 0:
                audio = self.__MODEL__.apply_tts(
                    text=text,
                    speaker=self.__SPEAKER__,
                    sample_rate=self.__SAMPLERATE__,
                    put_accent=self.__PUT_ACCENT__,
                    put_yo=self.__PUT_YO__,
                    put_stress_homo=self.__PUT_STRESS_HOMO__,
                    put_yo_homo=self.__PUT_YO_HOMO__,
                )
            else:
                audio = self.__MODEL_EN__.apply_tts(
                    text=text,
                    speaker=self.__SPEAKER_EN__,
                    sample_rate=self.__SAMPLERATE__,
                )

            # ✅ Настройка sounddevice
            audio = audio.squeeze()  # Убираем лишние размерности
            sd.play(audio, samplerate=48000)
            sd.wait()
        except Exception as e:
            print(f"⚠️ TTS fail: {e}")


tts = TTS(
    speaker=setting.conf_tts.SPEAKER,
    speaker_en=setting.conf_tts.SPEAKER_EN,
    device=setting.conf_tts.DEVICE,
    samplerate=setting.conf_tts.samplerate,
    put_accent=setting.conf_tts.put_accent,
    put_yo=setting.conf_tts.put_yo,
    put_stress_homo=setting.conf_tts.put_stress_homo,
    put_yo_homo=setting.conf_tts.put_yo_homo,
)
