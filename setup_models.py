"""Run once with internet on the development computer; models are local afterward."""
from pathlib import Path
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
root = Path(__file__).resolve().parent
models = root / 'models'
models.mkdir(exist_ok=True)
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu').save(str(models / 'minilm'))
print('Saved MiniLM to models/minilm')
snapshot_download(repo_id='Systran/faster-whisper-tiny.en', local_dir=str(models / 'whisper-tiny-en'))
print('Saved offline CPU Whisper model to models/whisper-tiny-en')
