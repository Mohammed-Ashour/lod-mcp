import pytest

from server import tools
from server.api import LODNotFoundError

RAW_ENTRY = {
    "entry": {
        "lemma": "Haus",
        "partOfSpeech": "SUBST",
        "ipa": "hæːʊs",
        "audioFiles": [{"ogg": "https://example.com/entry.ogg"}],
        "videos": [{"url": "https://example.com/sign.mp4"}],
        "microStructures": [
            {
                "grammaticalUnits": [
                    {
                        "meanings": [
                            {
                                "targetLanguages": {
                                    "en": {
                                        "parts": [
                                            {"type": "translation", "content": "house"},
                                            {"type": "semanticClarifier", "content": "building"},
                                        ]
                                    },
                                    "de": {
                                        "parts": [
                                            {"type": "translation", "content": "Haus"},
                                        ]
                                    },
                                },
                                "examples": [
                                    {
                                        "parts": [
                                            {
                                                "type": "text",
                                                "parts": [
                                                    {"type": "word", "content": "eist"},
                                                    {
                                                        "type": "inflectedHeadword",
                                                        "content": "Haus",
                                                    },
                                                ],
                                            }
                                        ]
                                    }
                                ],
                                "inflection": {
                                    "forms": [
                                        {"content": "Haiser"},
                                        {"content": "Haus"},
                                    ]
                                },
                            },
                            {
                                "targetLanguages": {
                                    "en": {
                                        "parts": [
                                            {"type": "translation", "content": "household"},
                                            {"type": "semanticClarifier", "content": "family"},
                                        ]
                                    }
                                },
                                "examples": [],
                                "inflection": {"forms": []},
                            },
                        ]
                    }
                ]
            }
        ],
    }
}

RAW_VERB_ENTRY = {
    "entry": {
        "lemma": "goen",
        "partOfSpeech": "VRB",
        "tables": {
            "verbConjugation": {
                "@attributes": {
                    "id": "GOEN1",
                    "model": "GOEN1",
                    "separableVerb": "no",
                },
                "infinitive": "goen",
                "pastParticiple": "gaangen / gaang",
                "auxiliaryVerb": "sinn",
                "indicative": {
                    "present": {
                        "p1": "ginn",
                        "p2": "gees",
                        "p3": "geet",
                        "p4": "ginn",
                        "p5": "gitt",
                        "p6": "ginn",
                    },
                    "pastSimple": {
                        "p1": "goung",
                        "p2": "goungs",
                    },
                    "presentPerfect": {
                        "p1": "si gaangen / gaang",
                    },
                    "pastPerfect": {
                        "p1": "war gaangen / gaang",
                    },
                },
                "conditional": {
                    "presentSimple": {
                        "p1": "géing",
                        "p2": "géings",
                    },
                    "presentPerfect": {
                        "p1": "géif / géing goen",
                    },
                    "pastPerfect": {
                        "p1": "wier gaangen / gaang",
                    },
                },
                "imperative": {
                    "present": {
                        "p2": "géi!",
                        "p5": "gitt!",
                    }
                },
            }
        },
    }
}


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    tools.cache.clear()
    yield
    tools.cache.clear()


def test_search_word_brief_normalizes_pos_labels(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tools,
        "search_api",
        lambda word: {
            "results": [
                {"id": "HAUS1", "word_lb": "Haus", "pos": "SUBST+N"},
                {"id": "HAUSEN1", "word_lb": "hausen", "pos": "VRB"},
            ]
        },
    )

    assert tools.search_word_brief("haus") == {
        "HAUS1": "Haus (N)",
        "HAUSEN1": "hausen (V)",
    }


def test_autocomplete_filters_non_luxembourgish_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tools,
        "suggest_api",
        lambda prefix: {
            "items": [
                {"word": "ha", "lang": "nl"},
                {"word": "hal", "lang": "lb"},
                {"word": "ham", "lang": "en"},
                {"word": "har", "lang": "lb"},
            ]
        },
    )

    assert tools.autocomplete("ha", limit=10) == "hal, har"


def test_get_entry_and_get_entries_share_the_same_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tools, "entry_api", lambda lod_id: RAW_ENTRY)

    single = tools.get_entry("HAUS1", langs="en,de", max_examples=1)
    batch = tools.get_entries(["HAUS1"], langs="en,de", max_examples=1)

    assert single == {
        "id": "HAUS1",
        "w": "Haus",
        "pos": "SUBST",
        "ipa": "hæːʊs",
        "tr": {
            "en": "house building; household family",
            "de": "Haus",
        },
        "ex": ["eist Haus"],
        "infl": "Haiser, Haus",
        "audio": True,
        "sign": True,
    }
    assert batch == {"HAUS1": single}
    assert tools.get_def("HAUS1", "en") == "Haus: house building; household family"
    assert tools.get_defs(["HAUS1"], "en") == {"HAUS1": "Haus: house building; household family"}


def test_get_conjugation_and_get_conjugations_share_the_same_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tools, "entry_api", lambda lod_id: RAW_VERB_ENTRY)

    single = tools.get_conjugation("GOEN1")
    batch = tools.get_conjugations(["GOEN1"])

    assert single == {
        "id": "GOEN1",
        "w": "goen",
        "pos": "VRB",
        "inf": "goen",
        "pp": "gaangen / gaang",
        "aux": "sinn",
        "sep": False,
        "ind": {
            "prs": {
                "p1": "ginn",
                "p2": "gees",
                "p3": "geet",
                "p4": "ginn",
                "p5": "gitt",
                "p6": "ginn",
            },
            "pst": {
                "p1": "goung",
                "p2": "goungs",
            },
            "pf": {
                "p1": "si gaangen / gaang",
            },
            "plf": {
                "p1": "war gaangen / gaang",
            },
        },
        "cnd": {
            "prs": {
                "p1": "géing",
                "p2": "géings",
            },
            "pf": {
                "p1": "géif / géing goen",
            },
            "plf": {
                "p1": "wier gaangen / gaang",
            },
        },
        "imp": {
            "p2": "géi!",
            "p5": "gitt!",
        },
    }
    assert batch == {"GOEN1": single}


def test_get_conjugation_returns_not_conjugated_for_non_verbs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tools, "entry_api", lambda lod_id: RAW_ENTRY)

    assert tools.get_conjugation("HAUS1") == {
        "error": {
            "type": "not_conjugated",
            "message": "No verb conjugation available for HAUS1",
        }
    }


def test_get_entry_returns_structured_error_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_not_found(lod_id: str):
        raise LODNotFoundError("LOD entry not found: UNKNOWN1", status_code=404)

    monkeypatch.setattr(tools, "entry_api", raise_not_found)

    assert tools.get_entry("UNKNOWN1") == {
        "error": {
            "type": "not_found",
            "message": "LOD entry not found: UNKNOWN1",
            "status": 404,
        }
    }
