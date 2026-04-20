from huggingface_hub import hf_hub_download
from config.env_config import env

def download_base_model():
    print(f"Downloading {env.MODEL_BASE}/{env.MODEL_BASE_FILE}...")
    hf_hub_download(
        repo_id=env.MODEL_BASE,
        filename=env.MODEL_BASE_FILE,
    )
    print("Download complete!")


# def download_detect_model():
#     print(f"Downloading {env.MODEL_DETECT}/{env.MODEL_DETECT_FILE}...")
#     hf_hub_download(
#         repo_id=env.MODEL_DETECT,
#         filename=env.MODEL_DETECT_FILE,
#     )
#     print("Download complete!")


if __name__ == "__main__":
    download_base_model()
    # download_detect_model()