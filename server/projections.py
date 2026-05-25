"""Projection helpers for compact LOD MCP responses."""

from __future__ import annotations

from typing import Any, Iterable

TRANSLATION_PART_TYPES = {"translation", "semanticClarifier"}
EXAMPLE_PART_TYPES = {"word", "inflectedHeadword"}


def compact(obj: Any) -> Any:
    """Remove null and empty values recursively."""
    if isinstance(obj, dict):
        return {
            key: compact(value)
            for key, value in obj.items()
            if value is not None and value != [] and value != {} and value != ""
        }
    if isinstance(obj, list):
        return [compact(value) for value in obj]
    return obj


def _iter_meanings(entry: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Yield every meaning in an entry."""
    for micro_structure in entry.get("microStructures", []):
        for grammatical_unit in micro_structure.get("grammaticalUnits", []):
            yield from grammatical_unit.get("meanings", [])


def _requested_langs(langs: str) -> list[str]:
    """Normalize the requested languages string."""
    return [lang.strip()[:2] for lang in langs.split(",") if lang.strip()]


def _translation_text(parts: list[dict[str, Any]]) -> str:
    """Join translation fragments into a compact string."""
    return " ".join(
        part.get("content", "")
        for part in parts
        if part.get("type") in TRANSLATION_PART_TYPES
    ).strip()


def extract_translations(entry: dict[str, Any], langs: str) -> dict[str, str]:
    """Extract translations for the requested languages."""
    requested_langs = set(_requested_langs(langs))
    translations: dict[str, list[str]] = {}

    for meaning in _iter_meanings(entry):
        for lang, content in meaning.get("targetLanguages", {}).items():
            if lang not in requested_langs:
                continue

            text = _translation_text(content.get("parts", []))
            if not text:
                continue

            translations.setdefault(lang, [])
            if text not in translations[lang]:
                translations[lang].append(text)

    return {lang: "; ".join(items[:3]) for lang, items in translations.items()}


def extract_examples(entry: dict[str, Any], max_examples: int) -> list[str]:
    """Extract example sentences."""
    if max_examples <= 0:
        return []

    examples: list[str] = []
    for meaning in _iter_meanings(entry):
        for example in meaning.get("examples", []):
            if len(examples) >= max_examples:
                return examples

            for part in example.get("parts", []):
                if part.get("type") != "text":
                    continue

                words = [
                    nested.get("content", "")
                    for nested in part.get("parts", [])
                    if nested.get("type") in EXAMPLE_PART_TYPES
                ]
                if words:
                    examples.append(" ".join(words))
                    break

    return examples


def extract_inflections(entry: dict[str, Any]) -> str:
    """Extract compact inflection forms."""
    forms: list[str] = []
    for meaning in _iter_meanings(entry):
        for form in meaning.get("inflection", {}).get("forms", []):
            content = form.get("content")
            if content:
                forms.append(content)

    if not forms:
        return ""

    return ", ".join(list(dict.fromkeys(forms))[:5])


def extract_flags(entry: dict[str, Any]) -> dict[str, bool]:
    """Extract compact media flags."""
    flags: dict[str, bool] = {}
    if entry.get("audioFiles"):
        flags["audio"] = True
    if entry.get("videos"):
        flags["sign"] = True
    return flags


def project_entry(
    data: dict[str, Any],
    lod_id: str,
    langs: str = "de,fr,en",
    max_examples: int = 2,
) -> dict[str, Any]:
    """Project a raw LOD entry response into the compact MCP shape."""
    entry = data.get("entry", {})
    result: dict[str, Any] = {
        "id": lod_id,
        "w": entry.get("lemma"),
        "pos": entry.get("partOfSpeech"),
        "ipa": entry.get("ipa"),
    }

    translations = extract_translations(entry, langs)
    if translations:
        result["tr"] = translations

    examples = extract_examples(entry, max_examples)
    if examples:
        result["ex"] = examples

    inflections = extract_inflections(entry)
    if inflections:
        result["infl"] = inflections

    result.update(extract_flags(entry))
    return compact(result)


def project_definition(data: dict[str, Any], lod_id: str, lang: str = "en") -> str:
    """Project a raw LOD entry response into a minimal single-language definition."""
    entry = data.get("entry", {})
    word = entry.get("lemma", lod_id)

    translations: list[str] = []
    for meaning in _iter_meanings(entry):
        target = meaning.get("targetLanguages", {}).get(lang)
        if not target:
            continue

        text = _translation_text(target.get("parts", []))
        if text and text not in translations:
            translations.append(text)

    if translations:
        return f"{word}: " + "; ".join(translations[:3])
    return f"{word}: No {lang} translation available"
