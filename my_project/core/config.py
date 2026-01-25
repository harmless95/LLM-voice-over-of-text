from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigTwitch(BaseModel):
    token: str
    username: str
    channel: str
    client_id: str


class ModelLLM(BaseModel):
    MODEL_REPO: str = "snakers4/silero-models"
    MODEL_NAME: str = "silero_tts"
    LANGUAGE: str = "ru"  # ru / en
    LANGUAGE_EN: str = "en"
    SPEAKER_VERSION: str = "v5_ru"
    SPEAKER_VERSION_EN: str = "v3_en"


class ConfigTTS(BaseModel):
    samplerate: int = 48000
    put_accent: bool = True
    put_yo: bool = True
    put_stress_homo: bool = True
    put_yo_homo: bool = True

    # константы голосов, поддерживаемых в silero
    SPEAKER_AIDAR: ClassVar[str] = "aidar"
    SPEAKER_BAYA: ClassVar[str] = "baya"
    SPEAKER_KSENIYA: ClassVar[str] = "kseniya"
    SPEAKER_XENIA: ClassVar[str] = "xenia"
    SPEAKER_RANDOM: ClassVar[str] = "random"
    SPEAKER: ClassVar[str] = SPEAKER_XENIA
    SPEAKER_EN: str = "en_0"

    # константы девайсов для работы torch
    DEVICE_CPU: ClassVar[str] = "cpu"
    DEVICE_CUDA: ClassVar[str] = "cuda"
    DEVICE_VULKAN: ClassVar[str] = "vulkan"
    DEVICE_OPENGL: ClassVar[str] = "opengl"
    DEVICE_OPENCL: ClassVar[str] = "opencl"
    DEVICE: ClassVar[str] = DEVICE_CUDA


class ConfigSTT(BaseModel):
    path_model: str = BASE_DIR / "data_models/vosk/vosk-model-small-ru-0.22"
    path_model_translate: str = BASE_DIR / "data_models/helsinki_nlp/"
    samplerate: int = 16000
    blocksize: int = 8000
    device: int | None = None
    dtype: str = "int16"
    channels: int = 1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    conf_tw: ConfigTwitch
    conf_tts: ConfigTTS = ConfigTTS()
    conf_stt: ConfigSTT = ConfigSTT()
    model: ModelLLM = ModelLLM()


setting = Settings()
