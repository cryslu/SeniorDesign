import numpy as np

def best_similarity(answer_chunks, references, encode):
    """Return maximum cosine similarity over response chunks and references."""
    if not answer_chunks or not references:
        return 0.0
    a = encode(answer_chunks)
    b = encode(references)
    return float(np.max(a @ b.T))
