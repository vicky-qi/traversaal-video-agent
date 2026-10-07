"""Rewrite narration into the text the TTS voice should read, without changing its meaning.

Kokoro reads some written forms wrongly ("ROI" -> "roy", "$2.3B" -> "dollar two point three bee",
"2024-2025" -> "... dash ...", "2025" -> "two thousand twenty-five"). Captions keep the original
text; only the voice gets the rewritten version.

Usage as a module: from speech_text import to_speech  ->  (tts_text, warnings)
Usage as a script:
  python tools/speech_text.py "Some sentence with ROI in 2025."   # one sentence
  python tools/speech_text.py --run runs/<slug>                  # every narration line of a run
Both print the spoken text and Kokoro's phonemes (what the voice will actually say).
Respellings: templates/pronunciations.json (all videos), overridden by
runs/<slug>/pronunciations.json (one video).
"""
import json
import re
import sys
from pathlib import Path

LEXICON_PATH = Path(__file__).resolve().parent.parent / "templates" / "pronunciations.json"

ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
        "fifteen sixteen seventeen eighteen nineteen").split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

# All-caps words the voice already says as a word, not letter by letter.
SAY_AS_WORD = {"NASA", "NATO", "GAAP", "OPEC", "FIFA", "UNESCO", "UNICEF", "NAFTA", "FEMA",
               "EBITDA", "COVID", "SWOT", "LIDAR", "RAM", "CAPTCHA", "ASAP", "PIN", "OK"}
# Single-letter-safe acronyms Kokoro already spells correctly; left alone to keep text readable.
ALREADY_SPELLED = {"AI", "US", "UK", "EU", "CEO", "CFO", "CTO", "LLM", "HR", "GDP", "USD",
                   "KPI", "IT", "PC", "TV", "UCLA", "MBA", "MSBA", "API", "B2B", "B2C"}

SCALE = {"K": "thousand", "M": "million", "B": "billion", "T": "trillion"}
ABBREV = {"vs.": "versus", "vs": "versus", "e.g.": "for example", "i.e.": "that is",
          "etc.": "and so on", "approx.": "approximately", "&": "and", "24/7": "twenty-four seven",
          "50/50": "fifty-fifty", "and/or": "and or"}


def two_digits(n):
    if n < 20:
        return ONES[n]
    return TENS[n // 10] + ("" if n % 10 == 0 else "-" + ONES[n % 10])


def year_words(y):
    """2025 -> 'twenty twenty-five', 2005 -> 'two thousand five', 1999 -> 'nineteen ninety-nine'."""
    hi, lo = divmod(y, 100)
    if y % 1000 < 10 and y >= 2000:
        return "two thousand" + ("" if y % 1000 == 0 else " " + ONES[y % 1000])
    if lo == 0:
        return two_digits(hi) + " hundred"
    return two_digits(hi) + (" oh " + ONES[lo] if lo < 10 else " " + two_digits(lo))


def decade_words(y):
    """1990 -> 'nineteen nineties', 2020 -> 'twenty twenties', 2000 -> 'two thousands'."""
    if y % 100 == 0:
        return "two thousands" if y == 2000 else two_digits(y // 100) + " hundreds"
    w = year_words(y)
    last = w.rsplit(" ", 1)[-1]
    plural = last[:-1] + "ies" if last.endswith("y") else last + "s"
    return w.rsplit(" ", 1)[0] + " " + plural


def load_lexicon(run_dir=None):
    """Shared respellings, overridden by the run's own pronunciations.json if it has one."""
    lexicon = {}
    for path in (LEXICON_PATH, Path(run_dir) / "pronunciations.json" if run_dir else None):
        if path and path.exists():
            lexicon.update({k: v for k, v in json.loads(path.read_text()).items() if not k.startswith("_")})
    return lexicon


def to_speech(text, lexicon=None):
    lexicon = load_lexicon() if lexicon is None else lexicon
    s = text

    for written, spoken in lexicon.items():
        s = re.sub(rf"(?<!\w){re.escape(written)}(?!\w)", spoken, s)
    for written, spoken in ABBREV.items():
        s = re.sub(rf"(?<![\w/]){re.escape(written)}(?![\w/])", spoken, s, flags=re.I)

    # Ranges: 2024-2025, 2024–2025, 10-20% -> "to".
    s = re.sub(r"(\d)\s*[-–—]\s*(\d)", r"\1 to \2", s)
    # Money: $2.3B, $450M, $1.2 trillion, $50.
    s = re.sub(r"\$(\d[\d,]*(?:\.\d+)?)\s*([KMBT])\b",
               lambda m: f"{m.group(1)} {SCALE[m.group(2)]} dollars", s)
    s = re.sub(r"\$(\d[\d,]*(?:\.\d+)?)(\s+(?:thousand|million|billion|trillion))?",
               lambda m: f"{m.group(1)}{m.group(2) or ''} dollars", s)
    # Percent: 20%+ -> 20 percent or more; 58% -> 58 percent.
    s = re.sub(r"(\d)\s*%\s*\+", r"\1 percent or more", s)
    s = re.sub(r"(\d)\s*%", r"\1 percent", s)
    # Multipliers: 3x, 10X -> three times.
    s = re.sub(r"\b(\d+(?:\.\d+)?)[xX]\b", r"\1 times", s)
    # "No. 1" -> "number 1".
    s = re.sub(r"\bNo\.\s*(\d)", r"number \1", s)
    # Decades and years. A bare 4-digit number from 1900-2099 is read as a year.
    s = re.sub(r"\b(19|20)(\d)0s\b", lambda m: decade_words(int(m.group(1) + m.group(2) + "0")), s)
    s = re.sub(r"(?<![\d,.$])\b(19\d\d|20\d\d)\b(?!\d|[.,]\d|\s*(?:%|percent))",
               lambda m: year_words(int(m.group(1))), s)
    # Decimals: 1.2 -> "1 point 2", 2.35 -> "2 point 3 5" (the voice sometimes pauses at the dot).
    s = re.sub(r"(\d)\.(\d+)\b", lambda m: m.group(1) + " point " + " ".join(m.group(2)), s)
    # Acronyms: spell out letter by letter unless the voice already handles them.
    def acronym(m):
        word, plural = m.group(1), m.group(2) or ""
        if word in SAY_AS_WORD or word in ALREADY_SPELLED and not plural:
            return m.group(0)
        spelled = "-".join(word)  # hyphens stop a spelled "A" being read as the article "uh"
        return spelled + ("'s" if plural else "")
    s = re.sub(r"\b([A-Z]{2,6})(s)?\b", acronym, s)

    warnings = [f"symbol {tok!r} may be read aloud oddly"
                for tok in re.findall(r"\S*[/#@+=<>~^|\\]\S*", s)]
    return s, warnings


def phonemes(text):
    try:
        from kokoro_onnx.tokenizer import Tokenizer
    except ImportError:
        return "(phonemes unavailable: run through tools/env.sh)"
    return Tokenizer().phonemize(text, "en-us")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--run"]:
        run = Path(sys.argv[2])
        lexicon = load_lexicon(run)
        spec = json.loads((run / "scenes.json").read_text())
        items = [(f"{s['scene_id']}/{l['id']}", l["text"]) for s in spec["scenes"] for l in s["narration"]]
    else:
        lexicon = load_lexicon()
        items = [("", a) for a in sys.argv[1:]]
    for label, text in items:
        out, warns = to_speech(text, lexicon)
        print(f"{label + ' ' if label else ''}{text}")
        if out != text:
            print(f"   spoken:   {out}")
        print(f"   phonemes: {phonemes(out)}")
        for w in warns:
            print(f"   WARN {w}")
