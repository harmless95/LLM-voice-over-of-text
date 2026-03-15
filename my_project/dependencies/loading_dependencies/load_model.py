import torch
from core.config import setting, logger

MODEL_DIR = setting.model.MODEL_DIR
FILE_T = setting.model.SPEAKER_VERSION

MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH_RU = MODEL_DIR / f"{FILE_T}.pt"
MODEL_URL_RU = setting.model.MODEL_URL_RU


def loading_model_ru():
    # 1. если файла нет — качаем
    if not MODEL_PATH_RU.exists():
        logger.info("Файл RU модели не найден, скачиваю: %s", MODEL_URL_RU)
        torch.hub.download_url_to_file(MODEL_URL_RU, str(MODEL_PATH_RU))
        logger.info("RU модель скачана в: %s", MODEL_PATH_RU)

    # 2. грузим из локального .pt
    logger.info("Загрузка RU TTS из файла: %s", MODEL_PATH_RU)
    model = torch.package.PackageImporter(str(MODEL_PATH_RU)).load_pickle(
        "tts_models", "model"
    )
    model.to(torch.device(setting.conf_tts.DEVICE))
    return model, None
