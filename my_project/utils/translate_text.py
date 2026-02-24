import re
from transliterate import translit
from num2words import num2words

from core.config import setting, logger
from core.model import translate_text_ru


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


def main_message(text: list) -> str | None:
    logger.info("Start translate text: %s", text)
    name_str = text[0]
    logger.info("Start translate user: %s", name_str)
    text_str = re.sub(pattern_text, text_re, name_str)
    text_final = re.sub(pattern_number, number_re, text_str)
    logger.info("Translation of a string or number of a username: %s", text_final)

    message_str = text[1]
    logger.info("Start translate message: %s", message_str)
    message_tran = re.sub(pattern_text, message_en, message_str)
    message_final = re.sub(pattern_number, number_re, message_tran)
    logger.info("Translation of a string or number of a message: %s", message_final)

    result = text_final + message_final
    check_message = message_final.split()[1]
    has_english = bool(re.search(r"[a-zA-Z]", check_message))

    if has_english:
        logger.error("Translation error: %s", message_final)
        return None

    logger.info("Finish translate: %s", result)

    return result
