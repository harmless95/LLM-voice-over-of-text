from fuzzywuzzy import fuzz

from core.config import logger
from core.constants import (
    COMMAND_START,
    COMMAND_STOP,
    COMMAND_STATUS,
    TTS_DEFAULT_LANG,
    TTS_EN_LANG,
)
from core.model import stt, translate_text


class Commands:
    def __init__(self, voice_queue):

        self.voice_queue = voice_queue
        self.flag_stt = False
        self.all_commands = {
            COMMAND_START: self.start_com,
            COMMAND_STOP: self.stop_com,
            COMMAND_STATUS: self.status_com,
        }

    def equ(self, text, needed):
        return fuzz.ratio(text.lower(), needed.lower()) >= 80

    def start_com(self):
        self.flag_stt = True
        logger.info("Start Бобр")

        result_text_en = "Режим бобра включен"
        self.voice_queue.put((result_text_en, TTS_DEFAULT_LANG))
        return

    def stop_com(self):
        self.flag_stt = False
        # stt.active = False
        logger.info("Stop Бобр")
        result_text_en = "Режим бобра отключён"
        self.voice_queue.put((result_text_en, TTS_DEFAULT_LANG))
        return

    def status_com(self):
        status = "активен" if self.flag_stt else "выключен"
        self.voice_queue.put((f"Режим перевода {status}", TTS_DEFAULT_LANG))

    def execute(self, text: str):
        for cm, func in self.all_commands.items():
            if self.equ(text=text, needed=cm):
                func()
                return

        if self.flag_stt:
            logger.info("Распознано: %s", text)
            try:
                en_text = translate_text(text_ru=text)
                if en_text:
                    self.voice_queue.put((en_text, TTS_EN_LANG))
            except Exception as e:
                logger.error("Ошибка при переводе: %s", e)
