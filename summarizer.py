import re
from collections import Counter


STOP_WORDS = frozenset(
    "a an and are as at be by for from has have in is it of on or that the to was were with".split()
)


def summarize(text: str, keyword: str, max_sentences: int = 3) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) >= 35]
    if not sentences:
        return text[:600].strip()
    words = [w.lower() for w in re.findall(r"[\w']+", text)]
    frequencies = Counter(w for w in words if w not in STOP_WORDS and len(w) > 2)
    terms = {w.lower() for w in re.findall(r"[\w']+", keyword)}

    def score(sentence: str) -> float:
        tokens = [w.lower() for w in re.findall(r"[\w']+", sentence)]
        return (sum(frequencies[w] for w in tokens) + 6 * sum(w in terms for w in tokens)) / max(len(tokens), 1)

    selected = sorted(sorted(range(len(sentences)), key=lambda i: score(sentences[i]), reverse=True)[:max_sentences])
    return " ".join(sentences[i] for i in selected)[:1200]
