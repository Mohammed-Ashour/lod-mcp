"""Part-of-speech normalization helpers."""

from __future__ import annotations

POS_SHORT_MAP = {
    "SUBST": "N",
    "SUBST+N": "N",
    "SUBST+F": "N",
    "SUBST+M": "N",
    "VRB": "V",
    "ADJ": "ADJ",
    "ADV": "ADV",
    "ART": "ART",
}


def normalize_pos(pos: str | None) -> str:
    """Normalize LOD POS tags into compact labels for MCP responses."""
    if not pos:
        return ""
    if pos in POS_SHORT_MAP:
        return POS_SHORT_MAP[pos]
    return POS_SHORT_MAP.get(pos.split("+", 1)[0], pos)
