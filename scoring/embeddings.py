"""Load an already-downloaded MiniLM model. No network calls permitted."""
from functools import lru_cache
from pathlib import Path
from sentence_transformers import SentenceTransformer
ROOT = Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def get_model():
    path = ROOT / 'models' / 'minilm'
    if not (path / 'modules.json').exists():
        raise RuntimeError('Offline MiniLM model missing. Run setup_models.py once on an internet-connected development machine.')
    return SentenceTransformer(str(path), device='cpu', local_files_only=True)

def encode(texts):
    return get_model().encode(texts, normalize_embeddings=True, convert_to_numpy=True)
