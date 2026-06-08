"""
Core Word Frequency Analysis Engine
=====================================
Handles all text processing, frequency counting, and statistical analysis.
"""

import re
import math
import unicodedata
from collections import Counter
from typing import Optional
from app.utils import STOPWORDS, clean_text


class WordFrequencyAnalyzer:
    """
    Production-grade word frequency analyzer.

    Features:
    - Unicode normalization
    - Stopword filtering
    - Statistical metrics
    - Reading time estimation
    - Sentence & paragraph analysis
    """

    AVERAGE_READING_WPM = 238  # average adult reading speed

    def __init__(self, remove_stopwords: bool = True, min_word_length: int = 2):
        self.remove_stopwords = remove_stopwords
        self.min_word_length = min_word_length

    def analyze(self, text: str, top_n: int = 50) -> dict:
        """
        Full analysis of a text string.

        Returns a dict with:
            - top_words       : list of {word, count, percentage}
            - total_words     : int
            - unique_words    : int
            - filtered_words  : int (after stopword removal)
            - avg_word_length : float
            - char_count      : int
            - sentence_count  : int
            - paragraph_count : int
            - reading_time_sec: float
            - lexical_density : float  (unique / total)
            - word_counts     : Counter (full raw counts)
        """
        if not text or not text.strip():
            return self._empty_result()

        # --- raw stats (before filtering) ---
        raw_words = self._tokenize(text)
        total_words = len(raw_words)
        char_count = len(text.replace(" ", "").replace("\n", ""))
        sentence_count = self._count_sentences(text)
        paragraph_count = self._count_paragraphs(text)
        reading_time_sec = round((total_words / self.AVERAGE_READING_WPM) * 60, 1)

        # --- filtered tokens ---
        tokens = self._filter(raw_words)
        filtered_count = len(tokens)

        # --- frequency counts ---
        counter = Counter(tokens)
        unique_words = len(counter)
        avg_word_length = (
            round(sum(len(w) for w in tokens) / filtered_count, 2)
            if filtered_count
            else 0
        )
        lexical_density = (
            round(unique_words / total_words, 4) if total_words else 0
        )

        # --- top N words ---
        top_n_words = counter.most_common(top_n)
        top_words = [
            {
                "word": word,
                "count": count,
                "percentage": round((count / filtered_count) * 100, 2)
                if filtered_count
                else 0,
            }
            for word, count in top_n_words
        ]

        # --- letter frequency (for bonus heatmap) ---
        letters = [c.lower() for c in text if c.isalpha()]
        letter_counter = Counter(letters)
        total_letters = sum(letter_counter.values())
        letter_freq = [
            {"letter": ch, "count": cnt, "percentage": round(cnt / total_letters * 100, 2)}
            for ch, cnt in sorted(letter_counter.items(), key=lambda x: -x[1])[:26]
        ]

        return {
            "top_words": top_words,
            "total_words": total_words,
            "filtered_words": filtered_count,
            "unique_words": unique_words,
            "avg_word_length": avg_word_length,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "reading_time_sec": reading_time_sec,
            "lexical_density": lexical_density,
            "word_counts": dict(counter),
            "letter_freq": letter_freq,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _tokenize(self, text: str) -> list[str]:
        """Lowercase, normalize unicode, strip punctuation, split."""
        text = unicodedata.normalize("NFKD", text)
        text = text.lower()
        # keep only alphabetic tokens (no numbers, no punctuation)
        tokens = re.findall(r"\b[a-z']+\b", text)
        # strip leading/trailing apostrophes (e.g. 'twas → twas)
        tokens = [t.strip("'") for t in tokens if t.strip("'")]
        return tokens

    def _filter(self, tokens: list[str]) -> list[str]:
        """Apply stopword and length filters."""
        result = []
        for token in tokens:
            if len(token) < self.min_word_length:
                continue
            if self.remove_stopwords and token in STOPWORDS:
                continue
            result.append(token)
        return result

    def _count_sentences(self, text: str) -> int:
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])

    def _count_paragraphs(self, text: str) -> int:
        paragraphs = re.split(r"\n\s*\n", text.strip())
        return len([p for p in paragraphs if p.strip()])

    def _empty_result(self) -> dict:
        return {
            "top_words": [],
            "total_words": 0,
            "filtered_words": 0,
            "unique_words": 0,
            "avg_word_length": 0,
            "char_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "reading_time_sec": 0,
            "lexical_density": 0,
            "word_counts": {},
            "letter_freq": [],
        }
