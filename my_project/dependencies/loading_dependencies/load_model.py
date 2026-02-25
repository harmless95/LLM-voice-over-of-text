import torch

from core.config import setting

LOADING_MODEL = torch.hub.load(
    repo_or_dir=setting.model.MODEL_REPO,
    model=setting.model.MODEL_NAME,
    language=setting.model.LANGUAGE,
    speaker=setting.model.SPEAKER_VERSION,
)
