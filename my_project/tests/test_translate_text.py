import re

from utils.translate_text import main_message


def test_main_message_returns_none_on_invalid_input():
    assert main_message([]) is None
    assert main_message(["only_username"]) is None


def test_main_message_basic_username_and_message():
    result = main_message(["User123", "привет"])
    assert isinstance(result, str)
    # Сообщение должно содержать хотя бы исходную часть текста сообщения
    assert "привет" in result
    # Цифры в нике должны быть преобразованы в слова, а не оставаться цифрами
    assert not re.search(r"\d", result)

