import torch

from core.config import setting

LOADING_MODEL_EN = torch.hub.load(
    repo_or_dir=setting.model.MODEL_REPO,
    model=setting.model.MODEL_NAME,
    language=setting.model.LANGUAGE_EN,
    speaker=setting.model.SPEAKER_VERSION_EN,
)
