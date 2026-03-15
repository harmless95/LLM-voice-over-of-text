from fuzzywuzzy import fuzz

from core.config import logger
from core.constants import (
    COMMAND_START,
    COMMAND_STOP,
    COMMAND_STATUS,
    TTS_DEFAULT_LANG,
    TTS_EN_LANG,
)
from core.model import translate_text


class Commands:
    def __init__(self, voice_queue):

        self.voice_queue = voice_queue
        self.flag_stt = False
        self.all_commands = {
            COMMAND_START: self.start_com,
            COMMAND_STOP: self.stop_com,
            COMMAND_STATUS: self.status_com,
        }

    def equ_score(self, text: str, needed: str) -> int:
        return fuzz.ratio(text.lower(), needed.lower())

    def equ(self, text, needed, score=90) -> bool:
        score_text = self.equ_score(text, needed)
        logger.warning("score: %s", score_text)
        return score_text >= score

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
        best_func = None
        best_score = 0
        text_split = text.split()
        if not text_split:
            return

        logger.info("split text: %s", text_split[0])

        if self.equ(text=text_split[0], needed="бобр"):
            command_part = " ".join(text_split[1:]) if len(text_split) > 1 else ""
            logger.info("Command бобр: %s", text)
            logger.info("Command handler Бобр: %s", text)

            if command_part:
                for cm, func in self.all_commands.items():
                    score = self.equ_score(text=command_part, needed=cm)
                    if score > best_score:
                        best_score = score
                        best_func = func

                if best_func is not None and best_score >= 80:
                    best_func()
                    return
            logger.info("Бобр не знает команду: %s", command_part)
        else:
            logger.info("Бобр услышал свое имя, но команды нет")
        if self.flag_stt:
            logger.info("Распознано: %s", text)
            try:
                en_text = translate_text(text_ru=text)
                if en_text:
                    self.voice_queue.put((en_text, TTS_EN_LANG))
            except Exception as e:
                logger.error("Ошибка при переводе: %s", e)
