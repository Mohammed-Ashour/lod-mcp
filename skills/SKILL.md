---
name: lod-lookup
description: Look up Luxembourgish words in LOD dictionary. Use for translations, definitions, pronunciation, conjugations, examples. Supports de/fr/en/pt/nl.
---

# LOD Dictionary API

Luxembourgish Online Dictionary API at `https://lod.lu/api`

## When to Use
- Luxembourgish word translations/definitions
- Pronunciation (IPA) lookup
- Conjugations/inflections
- Example sentences

## Rate Limits
**Wait 100ms between requests. Use sequential calls, not parallel.**

## Endpoints

| Endpoint | URL | Returns |
|----------|-----|---------|
| Search | `GET /api/en/search?query={word}&lang=lb` | Entry IDs |
| Suggest | `GET /api/en/suggest?query={prefix}` | Word suggestions |
| Entry | `GET /api/lb/entry/{lod_id}` | Full details |

**Header:** `Accept: application/json`

## Response Templates

### Search Response
```json
{
  "description": string,
  "results": [
    {
      "id": string,           // "HAUS1"
      "word_lb": string,      // "Haus"
      "pos": string,          // "SUBST+N" | "VRB" | "ADJ"
      "sign_language": boolean
    }
  ]
}
```

### Entry Response (Noun)
```json
{
  "entry": {
    "lod_id": string,              // "HAUS1"
    "lemma": string,               // "Haus"
    "partOfSpeech": string,        // "SUBST"
    "ipa": string,                 // "hæːʊs"
    "audioFiles": [{"ogg": url, "aac": url}],
    "microStructures": [{
      "grammaticalUnits": [{
        "meanings": [{
          "number": int,
          "inflection": {"forms": [{"content": string}]},
          "targetLanguages": {
            "{lang}": {
              "parts": [
                {"type": "translation", "content": string},
                {"type": "semanticClarifier", "content": string}
              ]
            }
          },
          "examples": [{
            "parts": [{
              "type": "text",
              "parts": [
                {"type": "word" | "inflectedHeadword", "content": string}
              ]
            }]
          }]
        }]
      }]
    }]
  }
}
```

### Entry Response (Verb)
Same as noun + `tables.verbConjugation`:
```json
{
  "tables": {
    "verbConjugation": {
      "infinitive": string,
      "pastParticiple": string,
      "auxiliaryVerb": string,     // "hunn" | "sinn"
      "indicative": {
        "present": {"p1": "...", "p2": "...", "p3": "...", "p4": "...", "p5": "...", "p6": "..."},
        "pastSimple": {...},
        "presentPerfect": {...}
      },
      "conditional": {...},
      "imperative": {...}
    }
  }
}
```

**Person keys:** p1=I, p2=you, p3=he/she, p4=we, p5=you(pl), p6=they

## Extraction Paths

| Data | Path |
|------|------|
| Word | `entry.lemma` |
| POS | `entry.partOfSpeech` |
| IPA | `entry.ipa` |
| Translations | `entry.microStructures[].grammaticalUnits[].meanings[].targetLanguages.{lang}.parts[].content` where `type == "translation"` |
| Examples | Concatenate `meanings[].examples[].parts[].parts[].content` where `type` in `["word", "inflectedHeadword"]` |
| Inflections | `meanings[].inflection.forms[].content` |
| Conjugations | `entry.tables.verbConjugation` (verbs only) |

**Languages:** `de`, `fr`, `en`, `pt`, `nl`

## POS Codes

| Code | Meaning |
|------|---------|
| `SUBST`/`SUBST+N`/`SUBST+F`/`SUBST+M` | Noun (neutral/feminine/masculine) |
| `VRB` | Verb |
| `ADJ` | Adjective |
| `ADV` | Adverb |
| `ART` | Article |

## Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| Not found | `results: []` or HTTP 404 | "No results for '{word}'" |
| No translation | `targetLanguages.{lang}` missing | Skip or "No {lang} translation" |
| Network error | Timeout | Retry once after 500ms |

## Examples

### Simple Translation
```
GET /api/en/search?query=schoul&lang=lb
→ {"results": [{"id": "SCHOUL1", "word_lb": "Schoul", "pos": "SUBST+F"}]}

GET /api/lb/entry/SCHOUL1
→ Extract: entry.lemma="Schoul", targetLanguages.en.parts=[{"type":"translation","content":"school"}]

Result: "Schoul (feminine noun): school"
```

### Batch Lookup (Sequential!)
```
For words: ["haus", "schoul", "bierg"]
  GET /api/en/search?query=haus&lang=lb
  [wait 100ms]
  GET /api/en/search?query=schoul&lang=lb
  [wait 100ms]
  GET /api/en/search?query=bierg&lang=lb
  [wait 100ms]
  Then fetch entries for each ID
```

### Verb Conjugation
```
GET /api/lb/entry/GOEN1
Extract from entry.tables.verbConjugation:
  infinitive: "goen"
  indicative.present: {p1:"ginn", p2:"gees", p3:"geet", ...}
  pastParticiple: "gaangen / gaang"
  auxiliaryVerb: "sinn"
```

## Quick Reference

**Test IDs:** HAUS1 (noun), SCHOUL1 (noun), GOEN1 (verb)

**Unicode:** Handle ë, é, ä, ü, Ë, É, Ä, Ü

**Curl:**
```bash
curl "https://lod.lu/api/en/search?query=haus&lang=lb" -H "Accept: application/json"
curl "https://lod.lu/api/lb/entry/HAUS1" -H "Accept: application/json"
```
