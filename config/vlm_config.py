"""
This module configures and initializes the Vision-Language Model (VLM)
using `llama_cpp` and `huggingface_hub`. It sets up the necessary
environment variables and loads the model components.
"""
import os

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava16ChatHandler
from huggingface_hub import hf_hub_download

from config import env

os.environ["HF_TOKEN"] = env.HFTOKEN
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

repo_id = env.MODEL_BASE

mmproj_path = hf_hub_download(
    repo_id=repo_id,
    filename=env.MODEL_BASE_MMPROJ,
)
"""
The path to the multimodal projection (mmproj) model file, downloaded
from Hugging Face Hub. This is used by the Llava chat handler.
"""

chat_handler = Llava16ChatHandler(
    clip_model_path=mmproj_path,
    verbose=False,
)
"""
The chat handler for the Llama model, configured for Llava 1.6.
It integrates the CLIP model for multimodal capabilities.
"""

VLM = Llama.from_pretrained(
    repo_id=repo_id,
    filename=env.MODEL_BASE_FILE,
    chat_handler=chat_handler,
    n_ctx=4096,
    n_batch=2048,
    n_gpu_layers=0 if env.MODE == 'cpu' else -1,
    n_threads=env.CORES,
    verbose=True
)
"""
The initialized Llama model instance, loaded with the specified base model file
and configured with the Llava chat handler for multimodal interactions.
"""
