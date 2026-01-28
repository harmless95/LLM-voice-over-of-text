from transformers import pipeline
from core.config import setting

model_translate = setting.conf_stt.path_model_translate
model_translate_ru = setting.conf_stt.path_model_translate_ru


# для docker там уже скачано и мы берем из кеша
translator = pipeline("translation", model=model_translate, device=0)
translator_ru = pipeline("translation", model=model_translate_ru, device=0)


def translate_text(text_ru: str):
    result = translator(text_ru)
    return result


def translate_text_ru(text_ru: str):
    result = translator_ru(text_ru)
    return result
