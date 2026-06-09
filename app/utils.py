"""
Utility helpers: stopword list, text cleaning.
"""

import re
import unicodedata

# -----------------------------------------------------------------------
# Comprehensive English stopword list (300+ words)
# -----------------------------------------------------------------------
# True grammatical function words only — articles, prepositions, conjunctions,
# pure auxiliary verbs. Personal pronouns, negations, and content words
# are intentionally kept so users see accurate counts in their charts.
STOPWORDS = {
    # Articles
    "a", "an", "the",
    # Prepositions
    "about", "above", "after", "against", "at", "before", "below",
    "between", "by", "during", "for", "from", "in", "into", "of",
    "off", "on", "out", "over", "through", "to", "under", "until",
    "up", "with", "within", "without",
    # Coordinating & subordinating conjunctions
    "and", "as", "because", "both", "but", "down", "either", "except",
    "if", "nor", "once", "or", "since", "so", "than", "that", "though",
    "unless", "until", "when", "where", "which", "while", "yet",
    # Pure auxiliary / linking verbs
    "be", "been", "being",
    "can", "cannot", "could", "did", "do", "does", "doing", "done",
    "had", "has", "have", "having",
    "is", "may", "might", "must", "shall", "should", "was", "were",
    "will", "would",
    # Common contractions (split artefacts from tokenizer)
    "s", "t", "re", "ve", "ll", "d", "m", "n",
}


def clean_text(text: str) -> str:
    """
    Normalize and lightly clean text before analysis:
    - Normalize Unicode (NFKD)
    - Replace smart quotes with standard ASCII
    - Collapse excessive whitespace
    """
    text = unicodedata.normalize("NFKD", text)
    # smart quotes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    # em/en dashes → space
    text = text.replace("\u2014", " ").replace("\u2013", " ")
    # collapse runs of whitespace (preserve newlines)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()
