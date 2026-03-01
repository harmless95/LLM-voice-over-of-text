import re
from transliterate import translit
from num2words import num2words

from core.config import setting, logger
from core.model import translate_text_ru
from utils.smile_data import SMILE_DESCRIPTIONS


pattern_text = r"([a-zA-Z]+)"
pattern_number = r"([+-]?\d+(?:\.\d+)?)"


def text_re(match):
    return f" {translit(match.group(0), "ru")} "


def number_re(match):
    try:
        result_number = f" {num2words(match.group(0), lang="ru")} "
    except KeyError:
        return ""
    return result_number


def message_en(match):
    return f" {translate_text_ru(match.group(0))} "


def smile_text(text: str):
    # Сортируем: сначала длинные (типа смайла-человечка), потом короткие :)
    sorted_smiles = sorted(
        SMILE_DESCRIPTIONS.items(),
        key=lambda x: len(x[0]),
        reverse=True,
    )

    for smile, description in sorted_smiles:
        text = text.replace(smile, description)

    logger.info("Check smile: %s", text)
    return text


def main_message(text: list) -> str | None:
    logger.info("Start translate text: %s", text)
    # Озвучиваем пользователей ник как читается не только строчно но числовые
    name_str = text[0]
    logger.info("Start translate user: %s", name_str)
    text_str = re.sub(pattern_text, text_re, name_str)
    text_final = re.sub(pattern_number, number_re, text_str)
    logger.info("Translation of a string or number of a username: %s", text_final)

    # Находим смайлы и выводим описание
    message_smile = smile_text(text=text[1])
    message_str = message_smile
    logger.info("Start translate message: %s", message_str)

    # Находим в сообщение англ слова или числа для озвучивания
    message_tran = re.sub(pattern_text, message_en, message_str)
    message_final = re.sub(pattern_number, number_re, message_tran)

    # Проверяем смог перевести англ слова если они есть
    has_english = bool(re.search(r"[a-zA-Z]", message_final))
    if has_english:
        message_final = re.sub(pattern_text, text_re, message_final)
        logger.error("Translation error: %s", message_final)
    logger.info("Translation of a string or number of a message: %s", message_final)

    result = text_final + message_final
    logger.info("Finish translate: %s", result)

    return result
