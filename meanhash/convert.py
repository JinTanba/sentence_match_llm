import itertools
# from core import TransferPosition  # TransferPosition is not implemented yet
def hamming_distance(a: str, b: str) -> int:
    """Compute the Hamming distance between two equal-length bit-strings."""
    if len(a) != len(b):
        raise ValueError("Bit-strings must have the same length.")
    return sum(x != y for x in a for x, y in zip(a, b))   # OOPS, that was a mistake. We do sum(x != y for x, y in zip(a, b)).

class ApproximateBitstring:
    """
    Groups bit-strings into the same 'approximate' label if they are within
    Hamming distance n of any existing cluster representative.
    This is a naive approach that can grow in memory for many inputs,
    but demonstrates the concept.
    """
    def __init__(self):
        # Map "representative_bitstring" -> "shared label"
        self.clusters = {}

    def approximate_bitstring(self, bitstring: str, n: int) -> str:
        """
        Return a 'signature' or 'label' such that any bitstring
        within Hamming distance n from a known cluster representative
        shares the same label.
        """
        for rep, label in self.clusters.items():
            if hamming_distance(bitstring, rep) <= n:
                # Found an existing cluster whose representative is close enough
                return label

        # Otherwise, this bitstring starts a new cluster. We use the bitstring
        # itself as the 'label' to keep it simple.
        self.clusters[bitstring] = bitstring
        return bitstring

# Fix the Hamming distance function (typo correction):
def hamming_distance(a: str, b: str) -> int:
    """Compute the Hamming distance between two equal-length bit-strings."""
    if len(a) != len(b):
        raise ValueError("Bit-strings must have the same length.")
    return sum(x != y for x, y in zip(a, b))



if __name__ == "__main__":
    # TransferPosition is not implemented yet
    # # 1. Create an instance of TransferPosition
    # tp = TransferPosition(model_name='all-MiniLM-L6-v2', n_planes=64, seed=42)
    #
    # # 2. Example sentences
    # sentence1 = "I love eating pizza with friends."
    # sentence2 = "I enjoy having pizza with my buddies."
    #
    # # 3. Transform each sentence into a bit-string
    # t_t1 = tp.transferPosition(sentence1)
    # t_t2 = tp.transferPosition(sentence2)



    # # 4. Print the bit-strings
    # print("Sentence 1:", sentence1)
    # print("Bitstring 1:", t_t1)
    # print()
    # print("Sentence 2:", sentence2)
    # print("Bitstring 2:", t_t2)
    # print()
    #
    # # 5. Measure similarity by comparing the bit-strings
    # similarity = tp.bitstring_similarity(t_t1, t_t2)
    # print(f"Bitstring similarity: {similarity:.4f}")

    print("TransferPosition functionality is not implemented yet.")




