import os
from typing import Any

import huggingface_hub.file_download
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava16ChatHandler
from tqdm import tqdm

from config import env

"""
Configuration and initialization for the Vision-Language Model (VLM).

This module manages the downloading of model weights from Hugging Face,
configures the execution environment, and initializes the multi-modal
VLM client.
"""

os.environ["HF_TOKEN"] = env.HFTOKEN
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"


class ProgressPrinter(tqdm):
    """
    Custom progress bar that prints updates every 5% interval.

    Provides filtered console output specifically designed for
    monitoring large model downloads.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.last_printed: int = 0

    def update(self, n: int = 1) -> None:
        """
        Updates the progress and prints status if a 5% milestone is reached.

        Args:
            n: The number of increments to add to the progress.
        """
        super().update(n)
        if self.total:
            percent: int = int((self.n / self.total) * 100)
            if percent >= self.last_printed + 5:
                print(f"Download progress: {percent}%", flush=True)
                self.last_printed = percent


huggingface_hub.file_download.tqdm = ProgressPrinter

PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR: str = os.path.join(PROJECT_ROOT, "models")
os.makedirs(CACHE_DIR, exist_ok=True)

repo_id: str = env.MODEL_BASE

mmproj_path: str = hf_hub_download(
    repo_id=repo_id,
    filename=env.MODEL_BASE_MMPROJ,
    cache_dir=CACHE_DIR,
)

chat_handler: Llava16ChatHandler = Llava16ChatHandler(
    clip_model_path=mmproj_path, verbose=False
)

VLM: Llama = Llama.from_pretrained(
    repo_id=repo_id,
    filename=env.MODEL_BASE_FILE,
    chat_handler=chat_handler,
    n_ctx=4096,
    n_batch=2048,
    n_gpu_layers=-1 if env.MODE == "gpu" else 0,
    n_threads=env.CORES,
    verbose=True,
    cache_dir=CACHE_DIR,
)
