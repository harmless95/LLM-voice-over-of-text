from core.constants import COMMAND_START, COMMAND_STOP, COMMAND_STATUS, TTS_DEFAULT_LANG, TTS_EN_LANG
from core.model import commands_stt
from core.model.commands_stt import Commands


class FakeQueue:
    def __init__(self):
        self.items: list[tuple[str, str]] = []

    def put(self, item):
        self.items.append(item)


def test_commands_start_stop_status_toggle_and_queue_messages():
    q = FakeQueue()
    cmd = Commands(voice_queue=q)

    # Старт
    cmd.start_com()
    assert cmd.flag_stt is True
    assert ("Режим бобра включен", TTS_DEFAULT_LANG) in q.items

    # Статус
    cmd.status_com()
    assert any("Режим перевода" in text for text, _ in q.items)

    # Стоп
    cmd.stop_com()
    assert cmd.flag_stt is False
    assert ("Режим бобра отключён", TTS_DEFAULT_LANG) in q.items


def test_commands_execute_triggers_translation_when_active():
    q = FakeQueue()
    cmd = Commands(voice_queue=q)
    cmd.flag_stt = True

    # Подменяем функцию перевода, чтобы не вызывать настоящую модель
    def fake_translate_text(text_ru: str) -> str:
        return "HELLO_WORLD"

    commands_stt.translate_text = fake_translate_text

    cmd.execute("какой-то текст")

    assert ("HELLO_WORLD", TTS_EN_LANG) in q.items


def test_commands_execute_recognizes_command_by_similarity():
    q = FakeQueue()
    cmd = Commands(voice_queue=q)

    # Специально с небольшой ошибкой в написании
    cmd.execute("бобр страрт")

    assert cmd.flag_stt is True

