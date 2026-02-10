from pathlib import Path
from huggingface_hub import hf_hub_download
from config.env_config import env

vlm_dir = Path(__file__).resolve().parent / "VLM"
vlm_dir.mkdir(exist_ok=True)


def download_model():
    models_dir = vlm_dir / f"models--{env.MODEL_BASE.replace('/', '--')}"
    snapshots_dir = models_dir / "snapshots"

    if snapshots_dir.exists():
        for snapshot in snapshots_dir.iterdir():
            if (snapshot / env.MODEL_BASE_FILE).exists():
                print(f"✅ Model already exists: {snapshot / env.MODEL_BASE_FILE}")
                return

    print(f"Downloading {env.MODEL_BASE}/{env.MODEL_BASE_FILE}...")
    hf_hub_download(
        repo_id=env.MODEL_BASE,
        filename=env.MODEL_BASE_FILE,
        cache_dir=str(vlm_dir),
    )
    print("Download complete!")


if __name__ == "__main__":
    download_model()