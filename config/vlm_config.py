import os

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava16ChatHandler
from huggingface_hub import hf_hub_download

from config.env_config import env

os.environ["HF_TOKEN"] = env.HFTOKEN
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

repo_id = env.MODEL_BASE

mmproj_path = hf_hub_download(
    repo_id=repo_id,
    filename=env.MODEL_BASE_MMPROJ,
)

chat_handler = Llava16ChatHandler(
    clip_model_path=mmproj_path,
    verbose=False,
)

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
