#!/usr/bin/env python3

import numpy as np
from sentence_transformers import SentenceTransformer
from datasketch import MinHash

model = SentenceTransformer('all-MiniLM-L6-v2')

###############################################################################
# Function: get_embedding
###############################################################################
def get_embedding(text: str) -> np.ndarray:
    """
    Converts a string `text` into a semantic embedding vector using a
    pre-loaded SentenceTransformer model, and then L2-normalizes the vector.
    (# NEW / CHANGED)
    """
    embedding = model.encode(text)
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding

###############################################################################
# Tokenization methods
###############################################################################
def tokens_by_rounding(embedding: np.ndarray, decimal_places: int = 3) -> list:
    """
    Round each float in the embedding to 'decimal_places' digits, convert to str.
    (# CHANGED default: decimal_places=3)
    """
    return [f"{round(val, decimal_places)}" for val in embedding.tolist()]

def tokens_by_binning(embedding: np.ndarray, bin_size: float = 0.01) -> list:
    """
    Discretize (bin) each float in the embedding according to 'bin_size'.
    (# CHANGED default: bin_size=0.01)
    """
    binned = [int(val / bin_size) for val in embedding]
    return [f"bin_{b}" for b in binned]

###############################################################################
# Function: get_minhash_signature
###############################################################################
def get_minhash_signature(
    embedding: np.ndarray,
    num_perm: int = 512,          # (# CHANGED from 128 -> 512)
    seed: int = 42,
    use_binning: bool = False,
    round_digits_or_bin_size=0.01 # (# CHANGED default bin size / decimal places
) -> MinHash:

    if use_binning:
        tokens = tokens_by_binning(embedding, bin_size=round_digits_or_bin_size)
    else:
        decimal_places = int(round_digits_or_bin_size)
        tokens = tokens_by_rounding(embedding, decimal_places)

    m = MinHash(num_perm=num_perm, seed=seed)
    for token in tokens:
        m.update(token.encode('utf-8'))
    return m

###############################################################################
# Function: transferPosition (単独のLSH)
###############################################################################
def transferPosition(
    text: str,
    num_perm: int = 512,              # (# CHANGED)
    use_binning: bool = False,
    round_digits_or_bin_size=0.01,
    seed: int = 42
) -> str:
    """
    1) text -> embedding
    2) embedding -> MinHash signature
    3) signatureを文字列化して返す
    """
    embedding = get_embedding(text)
    signature = get_minhash_signature(
        embedding,
        num_perm=num_perm,
        seed=seed,
        use_binning=use_binning,
        round_digits_or_bin_size=round_digits_or_bin_size
    )
    
    signature_str = "-".join(map(str, signature.hashvalues))
    return signature_str

###############################################################################
# Function: transferPosition_ensemble (複数のLSHをまとめる)
###############################################################################
def transferPosition_ensemble(
    text: str,
    num_perm: int = 512,              # (# CHANGED)
    ensemble_size: int = 10,          # (# CHANGED from 5 -> 10)
    use_binning: bool = False,
    round_digits_or_bin_size=0.01,
    base_seed: int = 42
) -> str:
    """
    複数の異なるシードで MinHash を作り、それらを結合した文字列シグネチャを返す。
    """
    embedding = get_embedding(text)

    signature_parts = []
    for i in range(ensemble_size):
        current_seed = base_seed + i * 101
        
        mh = get_minhash_signature(
            embedding,
            num_perm=num_perm,
            seed=current_seed,
            use_binning=use_binning,
            round_digits_or_bin_size=round_digits_or_bin_size
        )
        
        part_str = "-".join(map(str, mh.hashvalues))
        signature_parts.append(part_str)
    
    ensemble_signature = "_".join(signature_parts)
    return ensemble_signature

###############################################################################
# Function: calcSim (using cosine similarity on embeddings)
###############################################################################
def calcSim(text1: str, text2: str, threshold: float = 0.7) -> bool:
    """
    Checks if the semantic similarity (cosine) of two texts is above a threshold.
    """
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)

    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity >= threshold

###############################################################################
# Function: getLSH (LSHの結果をまとめて取得)
###############################################################################
def getLSH(
    text: str,
    num_perm: int = 512,               # (# CHANGED)
    ensemble_size: int = 10,           # (# CHANGED)
    use_binning: bool = False,
    round_digits_or_bin_size=0.01,     # (# CHANGED)
    base_seed: int = 42
) -> dict:
    """
    テキストに対して単一LSHとアンサンブルLSHの両方を実行し、結果を返す。
    """
    ensemble_result = transferPosition_ensemble(
        text,
        num_perm=num_perm,
        ensemble_size=ensemble_size,
        use_binning=use_binning,
        round_digits_or_bin_size=round_digits_or_bin_size,
        base_seed=base_seed
    )
    return hex(hash(ensemble_result))

###############################################################################
# Main (test/demo)
###############################################################################
if __name__ == "__main__":
    t1 = "i love ai"
    t2 = "I hate ai"

    # LSHの結果を取得
    lsh1 = getLSH(t1, use_binning=False, round_digits_or_bin_size=0.01)
    lsh2 = getLSH(t2, use_binning=False, round_digits_or_bin_size=0.01)

    print("LSH1:", lsh1)
    print("LSH2:", lsh2)

    hashed1 = hex(hash(lsh1))
    hashed2 = hex(hash(lsh2))

    print("Hash of LSH1:", hashed1)
    print("Hash of LSH2:", hashed2)
    print("Collision:", hashed1 == hashed2)

    # Check actual cosine similarity
    sim = calcSim(t1, t2, threshold=0.7)
    print("Cosine similarity >= 0.7 ? ", sim)
