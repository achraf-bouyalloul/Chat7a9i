from huggingface_hub import snapshot_download

# Télécharge le modèle LaBSE dans ./LaBSE
snapshot_download(repo_id="sentence-transformers/LaBSE", local_dir="./LaBSE")