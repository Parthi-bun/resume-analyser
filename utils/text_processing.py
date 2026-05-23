import re
from typing import Iterable, List, Set

import spacy
from spacy.lang.en.stop_words import STOP_WORDS


def load_language_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        return spacy.blank("en")


NLP = load_language_model()


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[^A-Za-z0-9+#./ -]", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def normalize_token(token: str) -> str:
    return re.sub(r"\s+", " ", token.lower()).strip()


def extract_keywords(text: str, limit: int = 30) -> List[str]:
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return []

    doc = NLP(cleaned_text)
    keywords: List[str] = []
    seen: Set[str] = set()

    for token in doc:
        value = normalize_token(token.text)
        if (
            not value
            or value in STOP_WORDS
            or token.is_punct
            or token.like_num
            or len(value) < 3
        ):
            continue

        lemma = normalize_token(token.lemma_ if token.lemma_ != "-PRON-" else token.text)
        if lemma not in seen:
            keywords.append(lemma)
            seen.add(lemma)

        if len(keywords) >= limit:
            break

    return keywords


def unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for item in items:
        normalized = normalize_token(item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(item)
    return ordered
