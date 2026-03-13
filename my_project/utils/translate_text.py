import re
from typing import Callable, Iterable, List

from transliterate import translit
from num2words import num2words

from core.config import setting, logger
from core.model import translate_text_ru
from utils.smile_data import SMILE_DESCRIPTIONS


_PATTERN_TEXT = r"([a-zA-Z]+)"
_PATTERN_NUMBER = r"([+-]?\d+(?:\.\d+)?)"


def _transliterate_en_to_ru(match: re.Match) -> str:
    return f" {translit(match.group(0), 'ru')} "


def _number_to_words_ru(match: re.Match) -> str:
    try:
        result_number = f" {num2words(match.group(0), lang='ru')} "
    except KeyError:
        return ""
    return result_number


def _translate_en_fragment_to_ru(match: re.Match) -> str:
    return f" {translate_text_ru(match.group(0))} "


def _replace_smiles(text: str) -> str:
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


def _prepare_username(raw_username: str) -> str:
    logger.info("Start translate user: %s", raw_username)
    text_str = re.sub(_PATTERN_TEXT, _transliterate_en_to_ru, raw_username)
    text_final = re.sub(_PATTERN_NUMBER, _number_to_words_ru, text_str)
    logger.info(
        "Translation of a string or number of a username: %s", text_final
    )
    return text_final


def _prepare_message_body(raw_message: str) -> str:
    # Находим смайлы и выводим описание
    message_with_smiles = _replace_smiles(text=raw_message)
    logger.info("Start translate message: %s", message_with_smiles)

    # Находим в сообщение англ слова или числа для озвучивания
    message_tran = re.sub(_PATTERN_TEXT, _translate_en_fragment_to_ru, message_with_smiles)
    message_final = re.sub(_PATTERN_NUMBER, _number_to_words_ru, message_tran)

    # Проверяем смог перевести англ слова если они есть
    has_english = bool(re.search(r"[a-zA-Z]", message_final))
    if has_english:
        message_final = re.sub(_PATTERN_TEXT, _transliterate_en_to_ru, message_final)
        logger.info("No translation: %s", message_final)

    logger.info(
        "Translation of a string or number of a message: %s", message_final
    )
    return message_final


def main_message(text: list) -> str | None:
    """
    Преобразует ник и текст сообщения в строку для озвучки.

    text: [username, message]
    """
    logger.info("Start translate text: %s", text)
    if not text or len(text) < 2:
        return None

    username, message = text[0], text[1]

    username_part = _prepare_username(username)
    message_part = _prepare_message_body(message)

    result = username_part + message_part
    logger.info("Finish translate: %s", result)

    return result
