from transformers import pipeline
from core.config import setting, logger

model_translate = setting.conf_stt.path_model_translate
model_translate_ru = setting.conf_stt.path_model_translate_ru


# для docker там уже скачано и мы берем из кеша
translator = pipeline("translation", model=model_translate, device=0)
translator_ru = pipeline("translation", model=model_translate_ru, device=0)


def translate_text(text_ru: str):
    logger.info("Start model translate en: %s", text_ru)
    result = translator(text_ru)
    if result and isinstance(result, list):
        return result[0].get("translation_text", "")
    return ""


def translate_text_ru(text_ru: str):
    logger.info("Start model translate ru: %s", text_ru)
    result = translator_ru(text_ru)
    if result and isinstance(result, list):
        return result[0].get("translation_text", "")
    return ""
