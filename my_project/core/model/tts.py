import torch
import sounddevice as sd

from core.config import setting, logger
from dependencies.loading_dependencies import loading_model_ru, loading_model_en


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
        self.__MODEL__, _ = loading_model_ru()
        self.__MODEL__.to(torch.device(device))

        self.__MODEL_EN__, _ = loading_model_en()
        self.__MODEL_EN__.to(torch.device(device))

        self.__SPEAKER__ = speaker
        self.__SPEAKER_EN__ = speaker_en
        self.__SAMPLERATE__ = samplerate
        self.__PUT_ACCENT__ = put_accent
        self.__PUT_YO__ = put_yo
        self.__PUT_STRESS_HOMO__ = put_stress_homo
        self.__PUT_YO_HOMO__ = put_yo_homo

    def text2speech(self, text: str, lang="ru"):
        try:
            logger.info("Говорит текст: %s язык озвучки: %s", text, lang)
            if lang == "ru":
                audio = self.__MODEL__.apply_tts(
                    text=text,
                    speaker=self.__SPEAKER__,
                    sample_rate=self.__SAMPLERATE__,
                    put_accent=self.__PUT_ACCENT__,
                    put_yo=self.__PUT_YO__,
                    put_stress_homo=self.__PUT_STRESS_HOMO__,
                    put_yo_homo=self.__PUT_YO_HOMO__,
                )

            elif lang == "en":
                audio = self.__MODEL_EN__.apply_tts(
                    text=text,
                    speaker=self.__SPEAKER_EN__,
                    sample_rate=self.__SAMPLERATE__,
                )
            else:
                logger.error("Incorrect data entry")

            # ✅ Настройка sounddevice
            audio = audio.squeeze()  # Убираем лишние размерности
            logger.info("Play audio: %s", audio)
            sd.play(audio, samplerate=48000)
            sd.wait()
        except Exception as e:
            logger.error("TTS fail: %s", e)


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
