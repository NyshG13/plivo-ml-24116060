"""Baseline tokenizer: raw UTF-8 bytes, vocab of 256. Simple, never fails on
unseen text — and treats a Devanagari character as 3 tokens. Think about
what that does to your model's context window and your token budget on the
Hindi part of the corpus.

You may replace this with anything you train ON THE PROVIDED CORPUS ONLY
(e.g., BPE), as long as:
  1. it can encode ARBITRARY UTF-8 text (byte-level fallback) and it is
     LOSSLESS: decode(encode(text)) == text, exactly. The scorer and the
     graders both verify this round-trip — a lossy tokenizer makes bpb
     meaningless and disqualifies the run.
  2. this file keeps exposing:  load() -> tokenizer object with
     .encode(str) -> list[int], .decode(list[int]) -> str, .vocab_size.
     train.py and evaluate.py call load() with NO arguments — keep any
     extra parameters optional.
  3. anything it needs is saved under your submission folder and loaded by
     load() with no internet. Grading runs with cwd = your folder; resolve
     saved files relative to __file__ to be safe.
"""
# import json


# class ByteTokenizer:
#     vocab_size = 256

#     def encode(self, text):
#         return list(text.encode("utf-8"))

#     def decode(self, ids):
#         return bytes(ids).decode("utf-8", errors="replace")

#     def save(self, path):
#         with open(path, "w") as f:
#             json.dump({"type": "byte"}, f)


# def load(path=None):
#     """Return the tokenizer used by evaluate.py. Replace as needed."""
#     return ByteTokenizer()


#TOKENIZER 1 
# import json
# import os
# from collections import Counter

# _VOCAB_FILE = os.path.join(os.path.dirname(__file__), "char_vocab.json")


# class CharByteTokenizer:
#     def __init__(self, extra_chars=None):
#         self.extra_chars = extra_chars or []
#         self.char_to_id = {ch: 256 + i for i, ch in enumerate(self.extra_chars)}
#         self.id_to_bytes = {i: bytes([i]) for i in range(256)}
#         for ch, tid in self.char_to_id.items():
#             self.id_to_bytes[tid] = ch.encode("utf-8")
#         self.vocab_size = 256 + len(self.extra_chars)

#     def encode(self, text):
#         out = []
#         for ch in text:
#             tid = self.char_to_id.get(ch)
#             if tid is not None:
#                 out.append(tid)
#             else:
#                 out.extend(ch.encode("utf-8"))
#         return out

#     def decode(self, ids):
#         raw = b"".join(self.id_to_bytes[i] for i in ids)
#         return raw.decode("utf-8", errors="replace")

#     def save(self, path):
#         with open(path, "w", encoding="utf-8") as f:
#             json.dump({"type": "char_byte", "extra_chars": self.extra_chars},
#                        f, ensure_ascii=False)


# def train_and_save(corpus_path, out_path=_VOCAB_FILE, max_extra=1500):
#     """Call this ONCE before train.py. Trained only on train_corpus.txt."""
#     text = open(corpus_path, encoding="utf-8").read()
#     counts = Counter(ch for ch in text if len(ch.encode("utf-8")) > 1)
#     most_common = [ch for ch, _ in counts.most_common(max_extra)]
#     tok = CharByteTokenizer(extra_chars=most_common)
#     tok.save(out_path)
#     print(f"trained char vocab: {len(most_common)} extra chars -> "
#           f"vocab_size={tok.vocab_size}")
#     return tok


# def load(path=None):
#     """train.py / evaluate.py call this with NO arguments."""
#     vocab_path = path or _VOCAB_FILE
#     if os.path.exists(vocab_path):
#         with open(vocab_path, encoding="utf-8") as f:
#             data = json.load(f)
#         return CharByteTokenizer(extra_chars=data.get("extra_chars", []))
#     return CharByteTokenizer(extra_chars=[])  # pure byte fallback if untrained


# if __name__ == "__main__":
#     import sys
#     train_and_save(sys.argv[1] if len(sys.argv) > 1 else "../data/train_corpus.txt")

#TOKENIZER 2 

import json
import os
from collections import Counter

_VOCAB_FILE = os.path.join(os.path.dirname(__file__), "char_vocab.json")


class CharByteTokenizer:
    def __init__(self, extra_chars=None):
        self.extra_chars = extra_chars or []
        self.char_to_id = {ch: 256 + i for i, ch in enumerate(self.extra_chars)}
        self.id_to_bytes = {i: bytes([i]) for i in range(256)}
        for ch, tid in self.char_to_id.items():
            self.id_to_bytes[tid] = ch.encode("utf-8")
        self.vocab_size = 256 + len(self.extra_chars)

    def encode(self, text):
        out = []
        for ch in text:
            tid = self.char_to_id.get(ch)
            if tid is not None:
                out.append(tid)
            else:
                out.extend(ch.encode("utf-8"))
        return out

    def decode(self, ids):
        raw = b"".join(self.id_to_bytes[i] for i in ids)
        return raw.decode("utf-8", errors="replace")

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"type": "char_byte", "extra_chars": self.extra_chars},
                       f, ensure_ascii=False)


def train_and_save(corpus_path, out_path=_VOCAB_FILE, max_extra=1500):
    """Call this ONCE before train.py. Trained only on train_corpus.txt."""
    text = open(corpus_path, encoding="utf-8").read()
    counts = Counter(ch for ch in text if len(ch.encode("utf-8")) > 1)
    most_common = [ch for ch, _ in counts.most_common(max_extra)]
    tok = CharByteTokenizer(extra_chars=most_common)
    tok.save(out_path)
    print(f"trained char vocab: {len(most_common)} extra chars -> "
          f"vocab_size={tok.vocab_size}")
    return tok


def load(path=None):
    """train.py / evaluate.py call this with NO arguments."""
    vocab_path = path or _VOCAB_FILE
    if os.path.exists(vocab_path):
        with open(vocab_path, encoding="utf-8") as f:
            data = json.load(f)
        return CharByteTokenizer(extra_chars=data.get("extra_chars", []))
    return CharByteTokenizer(extra_chars=[])  # pure byte fallback if untrained


if __name__ == "__main__":
    import sys
    train_and_save(sys.argv[1] if len(sys.argv) > 1 else "data/train_corpus.txt")