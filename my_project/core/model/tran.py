from transformers import pipeline

from core.config import setting

model_translate = setting.conf_stt.path_model_translate

# # берем из кеша
# translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-en", device=0)

# для docker там уже скачано и мы берем из кеша
translator = pipeline("translation", model=model_translate, device=0)


def translate_text(text_ru: str):
    result = translator(text_ru)
    return result
