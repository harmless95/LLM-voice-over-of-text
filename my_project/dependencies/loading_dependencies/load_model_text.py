from huggingface_hub import snapshot_download
import logging

from core.config import BASE_DIR

logging.basicConfig(level=logging.INFO)

# Загрузка модели RU -> EN
logging.info("Downloading RU-EN model...")

dir_file_en = BASE_DIR / "data_models/helsinki_nlp"
dir_file_ru = BASE_DIR / "data_models/helsinki_ru_nlp"

snapshot_download("Helsinki-NLP/opus-mt-ru-en", local_dir=dir_file_en)


# Загрузка модели EN -> RU
logging.info("Downloading EN-RU model...")

snapshot_download("Helsinki-NLP/opus-mt-en-ru", local_dir=dir_file_ru)
