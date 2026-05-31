"""
intake_agent.py — Converts customer free-text into a validated print brief.

Two-pass approach:
  Pass 1: deterministic regex + keyword extraction (fast, free, no model)
  Pass 2: qwen2.5:7b via Ollama if key fields are still missing (structured JSON prompt)

Returns a partial brief dict compatible with commissions/brief.py validate_brief().
Missing fields are filled with defaults by brief.py downstream.
"""

import re
import json
import sys
import pathlib
from typing import Optional

# ── commissions on path ───────────────────────────────────────────────────────
_PRINTER = pathlib.Path(__file__).parents[1]
if str(_PRINTER) not in sys.path:
    sys.path.insert(0, str(_PRINTER))
from commissions.brief import SMOKING_KEYWORDS, VALID_MATERIALS


# ── Config defaults (overridden by config.yaml in packaged version) ───────────
OLLAMA_HOST   = "http://localhost:11434"
INTAKE_MODEL  = "qwen2.5:7b"
LABOR_RATE    = 20.0
DEFAULT_COLOR = "natural"


# ── Keyword tables ────────────────────────────────────────────────────────────
SIZE_KEYWORDS = {
    "small":   ["small", "tiny", "mini", "little", "palm"],
    "medium":  ["medium", "medium-sized", "regular", "standard"],
    "large":   ["large", "big", "full-size", "oversized"],
}

MATERIAL_HINTS = {
    "petg":  ["petg", "flexible", "stronger", "water"],
    "abs":   ["abs", "heat resistant", "tough"],
    "tpu":   ["tpu", "rubber", "soft", "bendy", "flexible"],
    "resin": ["resin", "high detail", "smooth finish"],
    "pla":   ["pla"],
}

CUSTOMIZATION_KEYWORDS = {
    "logo":         ["logo", "brand", "emblem", "engraving", "engrave"],
    "text":         ["text", "name", "initials", "inscription", "words"],
    "color_change": ["color", "colour", "painted", "two-tone"],
    "custom_design":["design", "original", "from scratch", "custom shape"],
    "rush":         ["rush", "urgent", "asap", "today", "fast", "quick"],
}

QTY_PATTERN    = re.compile(r'\b(\d+)\s*(?:x|×|pieces?|units?|copies|qty|quantity)?\b', re.I)
NUMBER_WORDS   = {"one":1,"two":2,"three":3,"four":4,"five":5,
                  "six":6,"seven":7,"eight":8,"nine":9,"ten":10}


# ── Pass 1: deterministic extraction ─────────────────────────────────────────
def _extract_qty(text: str) -> int:
    for word, n in NUMBER_WORDS.items():
        if re.search(rf'\b{word}\b', text, re.I):
            return n
    matches = QTY_PATTERN.findall(text)
    candidates = [int(m) for m in matches if 1 <= int(m) <= 500]
    return candidates[0] if candidates else 1


def _extract_material(text: str) -> Optional[str]:
    lower = text.lower()
    # smoking items → enforce PETG minimum
    if any(kw in lower for kw in SMOKING_KEYWORDS):
        return "petg"
    for mat, hints in MATERIAL_HINTS.items():
        if any(h in lower for h in hints):
            return mat
    return None


def _extract_size(text: str) -> Optional[str]:
    lower = text.lower()
    for size, hints in SIZE_KEYWORDS.items():
        if any(h in lower for h in hints):
            return size
    return None


def _extract_customizations(text: str) -> list:
    lower = text.lower()
    found = []
    for key, hints in CUSTOMIZATION_KEYWORDS.items():
        if any(h in lower for h in hints):
            found.append(key)
    return found


def _is_smoking(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in SMOKING_KEYWORDS)


def _infer_job_type(text: str, customizations: list) -> str:
    if any(k in customizations for k in ["rush"]):
        return "urgent_rush"
    if any(k in customizations for k in ["custom_design", "logo", "text"]):
        return "design_heavy_oneoff"
    if _is_smoking(text):
        return "functional_custom_part"
    lower = text.lower()
    if any(w in lower for w in ["bracket","mount","enclosure","jig","tool","functional"]):
        return "functional_custom_part"
    return "commodity_decor"


def pass1(text: str) -> dict:
    qty     = _extract_qty(text)
    mat     = _extract_material(text)
    size    = _extract_size(text)
    customs = _extract_customizations(text)
    smoking = _is_smoking(text)
    jtype   = _infer_job_type(text, customs)

    brief = {
        "piece_name":     _clean_name(text),
        "quantity":       qty,
        "job_type":       jtype,
        "smoking":        smoking,
        "customizations": customs,
        "_confidence":    "high",
    }
    if mat:
        brief["material"] = {"type": mat}
    if size:
        brief.setdefault("market", {})["size"] = size

    # Check what's still missing
    missing = []
    if not mat:
        missing.append("material")
    if brief["piece_name"] in ("custom print", ""):
        missing.append("piece_name")

    brief["_missing"] = missing
    return brief


def _clean_name(text: str) -> str:
    """Extract a clean item name from the customer message."""
    stopwords = (
        r'\b(i want|i need|i have a file|i have|can you|could you|please|make me|'
        r'print me|print|just|only|need|want|a|an|the|some|me|my|qty|quantity|hey|hi)\b'
    )
    text = re.sub(stopwords, '', text, flags=re.I)
    text = re.sub(r'\b\d+\s*(x|×|pieces?|units?)\b', '', text, flags=re.I)
    # Strip trailing qualifiers like "in black petg" or "medium size"
    text = re.sub(r'\b(in|with|using|for)\s+(black|white|red|blue|green|petg|pla|abs|tpu|medium|large|small)\b.*', '', text, flags=re.I)
    text = re.sub(r'\s+', ' ', text).strip(' ,.')
    name = text.split(',')[0].split('.')[0].strip()[:60]
    return name or "custom print"


# ── Pass 2: LLM extraction (only if pass1 missing key fields) ─────────────────
OLLAMA_PROMPT = """Extract print job details from this customer message.
Return ONLY valid JSON with these fields (use null if unknown):

{{
  "piece_name": "short descriptive name",
  "quantity": <integer>,
  "material": "pla|petg|abs|tpu|resin|null",
  "size_hint": "small|medium|large|null",
  "customizations": ["logo","text","custom_design","rush"],
  "notes": "any special requests verbatim"
}}

Customer message: {message}

JSON only, no explanation:"""


def pass2(text: str, partial: dict) -> dict:
    """Call qwen2.5:7b to fill in fields that pass1 couldn't extract."""
    try:
        import urllib.request
        payload = json.dumps({
            "model":  INTAKE_MODEL,
            "prompt": OLLAMA_PROMPT.format(message=text),
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 256},
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
        raw = result.get("response", "").strip()
        # Extract JSON block
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return partial
        extracted = json.loads(match.group())

        # Merge into partial — only fill missing fields
        if extracted.get("piece_name") and partial.get("piece_name") in ("custom print", ""):
            partial["piece_name"] = extracted["piece_name"]
        if extracted.get("material") and "material" not in partial:
            partial["material"] = {"type": extracted["material"]}
        if extracted.get("quantity") and partial.get("quantity") == 1:
            partial["quantity"] = int(extracted["quantity"])
        if extracted.get("size_hint") and "market" not in partial:
            partial.setdefault("market", {})["size"] = extracted["size_hint"]
        if extracted.get("customizations"):
            existing = set(partial.get("customizations", []))
            partial["customizations"] = list(existing | set(extracted["customizations"]))
        if extracted.get("notes"):
            partial["notes"] = extracted["notes"]
        partial["_confidence"] = "medium"

    except Exception as e:
        partial["_llm_error"] = str(e)

    return partial


# ── Clarifying questions ──────────────────────────────────────────────────────
def clarifying_questions(brief: dict) -> list:
    """
    Return a list of questions to ask the customer for missing critical fields.
    Keeps it to 1-2 questions max — don't interrogate them.
    """
    questions = []
    missing = brief.get("_missing", [])

    if "material" in missing:
        if brief.get("smoking"):
            questions.append("What material? *(PETG or ABS recommended for this part type)*")
        else:
            questions.append("Any material preference? *(PLA is standard — or PETG for extra strength)*")

    if "piece_name" in missing or brief.get("piece_name") == "custom print":
        questions.append("What would you like to call this piece?")

    # Only ask for logo file if logo customization detected
    if "logo" in brief.get("customizations", []):
        questions.append("Do you have a logo file *(PNG or SVG)* or need design work?")

    return questions[:2]  # cap at 2 questions


# ── Main entry point ──────────────────────────────────────────────────────────
def parse(text: str, use_llm: bool = True) -> dict:
    """
    Full intake pipeline.
    Returns brief dict + metadata fields (_confidence, _missing, _questions).
    """
    brief = pass1(text)

    if brief["_missing"] and use_llm:
        brief = pass2(text, brief)

    brief["_questions"] = clarifying_questions(brief)
    return brief


if __name__ == "__main__":
    tests = [
        "I want a puffco proxy recycler, quad uptake, 2 of them in petg",
        "can you print me a small wall bracket, standard pla, just 1",
        "need 3 dab station trays with my logo on them asap",
        "I have a file, just print it in black petg, medium size",
    ]
    for t in tests:
        print(f"\nInput: {t}")
        result = parse(t, use_llm=False)
        print(f"  piece_name:     {result['piece_name']}")
        print(f"  quantity:       {result['quantity']}")
        print(f"  job_type:       {result['job_type']}")
        print(f"  material:       {result.get('material', {}).get('type', 'unknown')}")
        print(f"  smoking:        {result['smoking']}")
        print(f"  customizations: {result['customizations']}")
        print(f"  questions:      {result['_questions']}")
        print(f"  confidence:     {result['_confidence']}")
