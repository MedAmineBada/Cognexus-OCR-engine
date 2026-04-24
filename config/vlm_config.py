import os

from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava16ChatHandler
from tqdm import tqdm

from config import env

os.environ["HF_TOKEN"] = env.HFTOKEN
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"


# Custom tqdm that prints every 5%
class ProgressPrinter(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_printed = 0

    def update(self, n=1):
        super().update(n)
        if self.total:
            percent = int((self.n / self.total) * 100)
            if percent >= self.last_printed + 5:
                print(f"Download progress: {percent}%", flush=True)
                self.last_printed = percent


# Monkey patch tqdm
import huggingface_hub.file_download

huggingface_hub.file_download.tqdm = ProgressPrinter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(CACHE_DIR, exist_ok=True)

repo_id = env.MODEL_BASE

print(f"Starting download: {env.MODEL_BASE_MMPROJ}", flush=True)
mmproj_path = hf_hub_download(
    repo_id=repo_id,
    filename=env.MODEL_BASE_MMPROJ,
    cache_dir=CACHE_DIR,
)
print(f"Completed: {env.MODEL_BASE_MMPROJ}", flush=True)

chat_handler = Llava16ChatHandler(clip_model_path=mmproj_path, verbose=False)

print(f"Starting download: {env.MODEL_BASE_FILE}", flush=True)
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
print(f"Completed: {env.MODEL_BASE_FILE}", flush=True)
