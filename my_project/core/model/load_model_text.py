from huggingface_hub import snapshot_download
import logging

logging.basicConfig(level=logging.INFO)

snapshot_download(
    "Helsinki-NLP/opus-mt-ru-en", local_dir="../../data_models/helsinki_nlp"
)
