from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent


class ModelLLM(BaseModel):
    MODEL_REPO: str = "snakers4/silero-models"
    MODEL_NAME: str = "silero_tts"
    LANGUAGE: str = "ru"  # ru / en
    SPEAKER_VERSION: str = "ru_v3"  # ru_v3 / v4 / en_v3 и т.д.


class ConfigTTS(BaseModel):
    samplerate: int = 48_000

    # константы голосов, поддерживаемых в silero
    SPEAKER_AIDAR: ClassVar[str] = "aidar"
    SPEAKER_BAYA: ClassVar[str] = "baya"
    SPEAKER_KSENIYA: ClassVar[str] = "kseniya"
    SPEAKER_XENIA: ClassVar[str] = "xenia"
    SPEAKER_RANDOM: ClassVar[str] = "random"
    SPEAKER: ClassVar[str] = SPEAKER_KSENIYA

    # константы девайсов для работы torch
    DEVICE_CPU: ClassVar[str] = "cpu"
    DEVICE_CUDA: ClassVar[str] = "cuda"
    DEVICE_VULKAN: ClassVar[str] = "vulkan"
    DEVICE_OPENGL: ClassVar[str] = "opengl"
    DEVICE_OPENCL: ClassVar[str] = "opencl"
    DEVICE: ClassVar[str] = DEVICE_CPU


class ConfigSTT(BaseModel):
    path_model: str = BASE_DIR / "data_vosk/vosk-model-small-ru-0.22"
    samplerate: int = 16000
    blocksize: int = 8000
    device: int | None = None
    dtype: str = "int16"
    channels: int = 1


class Settings(BaseSettings):
    conf_tts: ConfigTTS = ConfigTTS()
    conf_stt: ConfigSTT = ConfigSTT()
    model: ModelLLM = ModelLLM()


setting = Settings()
