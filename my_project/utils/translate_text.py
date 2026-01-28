import re
from transliterate import translit
from num2words import num2words

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


def main_message(text: list) -> str:
    name_str = text[0]
    text_str = re.sub(pattern_text, text_re, name_str)
    text_number = re.sub(pattern_number, number_re, text_str)

    message_str = text[1]
    message_tran = re.sub(pattern_text, message_en, message_str)
    message_number = re.sub(pattern_number, number_re, message_tran)

    result = text_number + message_number

    return result
