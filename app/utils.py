"""
Utility helpers: stopword list, text cleaning.
"""

import re
import unicodedata

# -----------------------------------------------------------------------
# Comprehensive English stopword list (300+ words)
# -----------------------------------------------------------------------
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "get", "got", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only",
    "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "will", "with", "won't",
    "would", "wouldn't",
    # additional common filler
    "also", "just", "like", "even", "well", "back", "still", "way", "take",
    "every", "good", "new", "first", "last", "long", "great", "little",
    "own", "right", "big", "high", "different", "small", "large", "next",
    "early", "young", "important", "public", "private", "real", "best",
    "free", "sure", "know", "think", "go", "come", "see", "look", "want",
    "give", "use", "find", "tell", "ask", "seem", "feel", "try", "leave",
    "call", "keep", "let", "begin", "show", "hear", "play", "run", "move",
    "live", "believe", "hold", "bring", "happen", "write", "provide",
    "sit", "stand", "lose", "pay", "meet", "include", "continue", "set",
    "change", "lead", "understand", "watch", "follow", "stop",
    "create", "speak", "read", "spend", "grow", "open", "walk", "win",
    "offer", "remember", "love", "consider", "appear", "buy", "wait",
    "serve", "die", "send", "expect", "build", "stay", "fall", "cut",
    "reach", "kill", "remain", "suggest", "raise", "pass", "sell", "require",
    "report", "decide", "pull", "s", "t", "re", "ve", "ll", "d", "m",
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
