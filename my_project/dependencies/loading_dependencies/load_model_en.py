import torch
from core.config import setting, logger

MODEL_DIR = setting.model.MODEL_DIR
FILE_T = setting.model.SPEAKER_VERSION_EN

MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH_EN = MODEL_DIR / f"{FILE_T}.pt"
MODEL_URL_EN = setting.model.MODEL_URL_EN


def loading_model_en():
    # 1. если файла нет — качаем
    if not MODEL_PATH_EN.exists():
        logger.info("Файл EN модели не найден, скачиваю: %s", MODEL_URL_EN)
        torch.hub.download_url_to_file(MODEL_URL_EN, str(MODEL_PATH_EN))
        logger.info("EN модель скачана в: %s", MODEL_PATH_EN)

    # 2. грузим из локального .pt
    logger.info("Загрузка EN TTS из файла: %s", MODEL_PATH_EN)
    model = torch.package.PackageImporter(str(MODEL_PATH_EN)).load_pickle(
        "tts_models", "model"
    )
    model.to(torch.device(setting.conf_tts.DEVICE))
    return model, None
