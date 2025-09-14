# semid_en_g_v1.py  (G案: ECC丸め / ラウンド無し)
import os
import numpy as np
import hashlib, unicodedata, re
from sentence_transformers import SentenceTransformer

# ===== 推奨: 数値ゆれ低減（必要ならコメント解除） =====
# os.environ.setdefault("MKL_NUM_THREADS", "1")
# os.environ.setdefault("OMP_NUM_THREADS", "1")

# ===== 設定（固定値。全ノード同一に） =====
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # モデルは運用で固定推奨（revision固定推奨）
SEED_BASE  = "semaddr-en-g-v1"                         # 乱数の根っこ（変えないこと）
L = 2          # ヘッド数（2ヘッド×12bit = 24bit）
N = 24         # 各ヘッドのサインビット数（Golayの符号長）
EPS = 1e-5     # タイブレーク閾値（符号境界の決定性を強める）

# ===== ユーティリティ =====
def _hash32(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:4], "big")

def text_norm(s: str) -> str:
    # 文字正規化（互換分解ではなく NFC。必要なら NFKC + casefold に）
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\t", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sign_with_tie(u: np.ndarray, text_normed: str, head_idx: int) -> np.ndarray:
    """
    u: 実数 (N,). 0/1 に符号化。|u|<EPS は text+head+bit の SHA256 で固定。
    """
    bits = (u >= 0).astype(np.uint8)
    mask = np.abs(u) < EPS
    if mask.any():
        idxs = np.where(mask)[0]
        for j in idxs:
            h = hashlib.sha256(f"tb:v1|{text_normed}|{head_idx}|{j}".encode("utf-8")).digest()
            bits[j] = h[0] & 1
    return bits  # shape: (N,), dtype=uint8

# ===== 拡張Golay [24,12,8]（最近傍復号） =====
class Golay24:
    """
    拡張 Golay コード [24,12,8]
    - 構成: [23,12,7] の巡回Golayの生成多項式 g(x) で体系化エンコード → 偶数パリティ拡張
    - 復号: 4096 語のコードブックに対する最小ハミング距離（半径3まで確実訂正）
    """
    def __init__(self):
        # g(x) = x^11 + x^9 + x^7 + x^6 + x^5 + x + 1
        self.g = (1 << 11) | (1 << 9) | (1 << 7) | (1 << 6) | (1 << 5) | (1 << 1) | 1
        self.n = 23
        self.k = 12
        self.r = self.n - self.k  # 11
        self._codebook24 = self._build_codebook24()  # list[int] length 4096

    @staticmethod
    def _poly_deg(p: int) -> int:
        return p.bit_length() - 1

    def _poly_divmod(self, dividend: int, divisor: int):
        q = 0
        r = dividend
        dv_deg = self._poly_deg(divisor)
        while r and self._poly_deg(r) >= dv_deg:
            shift = self._poly_deg(r) - dv_deg
            q ^= (1 << shift)
            r ^= divisor << shift
        return q, r  # (quotient, remainder)

    def _encode23(self, m: int) -> int:
        # 体系化: c(x) = m(x) * x^r + rem( m(x)*x^r , g(x) )
        mshift = m << self.r
        _, rem = self._poly_divmod(mshift, self.g)
        return mshift ^ rem  # 23-bit int

    def _extend24(self, cw23: int) -> int:
        # 偶数パリティ拡張（全24bitの1の数を偶数に）
        parity = cw23.bit_count() & 1
        return cw23 | (parity << 23)  # parity は bit 23（MSB側）に置く

    def _build_codebook24(self):
        code23 = [self._encode23(m) for m in range(1 << self.k)]
        code24 = [self._extend24(cw) for cw in code23]
        return code24

    @staticmethod
    def _bits_to_int(bits: np.ndarray) -> int:
        # bits[j] が bit j（LSB）を表す前提
        v = 0
        # np.uint8 -> python int
        for j, b in enumerate(bits.tolist()):
            if b & 1:
                v |= (1 << j)
        return v

    def decode_to_msg12(self, bits: np.ndarray) -> int:
        """
        入力: 24bit の numpy 配列 {0,1}
        出力: 12bit メッセージ（0..4095）※最近傍（ハミング距離最小、同点は最小index）
        """
        v = self._bits_to_int(bits)
        best_idx = 0
        best_d = 1 << 30
        for idx, cw in enumerate(self._codebook24):
            d = (cw ^ v).bit_count()
            if d < best_d:
                best_d = d
                best_idx = idx
                if d == 0:
                    break
        return best_idx  # 12bit int

# ===== SemID（G案） =====
class SemID:
    def __init__(self, model_name: str = MODEL_NAME, seed_base: str = SEED_BASE):
        # 埋め込みモデル（CPU固定）
        # revision を固定するとより堅牢: SentenceTransformer(model_name, device="cpu", revision="<commit>")
        self.model = SentenceTransformer(model_name, device="cpu")
        self.seed_base = seed_base

        # 乱数から W を作る（埋め込み次元 d が分かってから列正規化）
        self.W = None  # shape: (L, d, N)

        # Golay 復号器（共有でOK）
        self.golay = Golay24()

    def _ensure_W(self, dim: int):
        if self.W is not None:
            return
        Ws = []
        for i in range(L):
            seed_w = _hash32(f"{self.seed_base}::head{i}::W")
            rng = np.random.RandomState(seed_w)
            W = rng.normal(size=(dim, N)).astype(np.float32)  # (d, 24)
            W /= (np.linalg.norm(W, axis=0, keepdims=True) + 1e-12)
            Ws.append(W)
        self.W = np.stack(Ws, axis=0)  # (L, d, 24)

    def embed(self, text: str):
        t = text_norm(text)
        x = self.model.encode([t], normalize_embeddings=True)[0].astype(np.float32)  # (d,)
        return t, x

    def id24(self, text: str) -> int:
        """
        2ヘッド×12bit を連結した 24bit ID を返す。
        """
        t, x = self.embed(text)
        self._ensure_W(x.shape[0])

        parts = []
        for i in range(L):
            u = x @ self.W[i]                 # (24,)
            bits = sign_with_tie(u, t, i)     # 0/1 × 24
            msg12 = self.golay.decode_to_msg12(bits)  # 0..4095
            parts.append(msg12)

        return (parts[0] << 12) | parts[1]

    def id_bytes(self, text: str) -> bytes:
        v = self.id24(text)
        return v.to_bytes(3, "big")

    def id_hex(self, text: str) -> str:
        return self.id_bytes(text).hex()

    def id_parts(self, text: str):
        """デバッグ用途: (head0の12bit, head1の12bit, 連結24bit)"""
        t, x = self.embed(text)
        self._ensure_W(x.shape[0])
        a = []
        for i in range(L):
            u = x @ self.W[i]
            bits = sign_with_tie(u, t, i)
            a.append(self.golay.decode_to_msg12(bits))
        return a[0], a[1], (a[0] << 12) | a[1]

# ========== 簡単デモ ==========
if __name__ == "__main__":
    sid = SemID()
    s1 = "It is sunny in Tokyo today."
    s2 = "Tokyo has clear skies today."
    s3 = "My dinner last night was curry."
    print("ID(s1):", sid.id_hex(s1))
    print("ID(s2):", sid.id_hex(s2))
    print("ID(s3):", sid.id_hex(s3))
