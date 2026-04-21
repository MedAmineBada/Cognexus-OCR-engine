import os

from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava16ChatHandler

from config import env

os.environ["HF_TOKEN"] = env.HFTOKEN
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# Define cache directory relative to project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # Go up from config/ to ocrengine/
CACHE_DIR = os.path.join(PROJECT_ROOT, "models")

# Ensure models directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

repo_id = env.MODEL_BASE

print(f"{repo_id} - {env.MODEL_BASE_MMPROJ} started downloading")
mmproj_path = hf_hub_download(
    repo_id=repo_id,
    filename=env.MODEL_BASE_MMPROJ,
    cache_dir=CACHE_DIR,
)
print(f"{repo_id} - {env.MODEL_BASE_MMPROJ} finished downloading")

chat_handler = Llava16ChatHandler(
    clip_model_path=mmproj_path,
    verbose=False,
)

print(f"{repo_id} - {env.MODEL_BASE_FILE} started downloading")
VLM = Llama.from_pretrained(
    repo_id=repo_id,
    filename=env.MODEL_BASE_FILE,
    chat_handler=chat_handler,
    n_ctx=4096,
    n_batch=2048,
    n_gpu_layers=0 if env.MODE == "cpu" else -1,
    n_threads=env.CORES,
    verbose=True,
    cache_dir=CACHE_DIR,
)
print(f"{repo_id} - {env.MODEL_BASE_FILE} finished downloading")
