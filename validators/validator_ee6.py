"""
EE-BENCH-6 „toimetamine“ (editing) validator, 15.11.2026.

Mõõdab, kas mudel oskab eestikeelset teksti keeleliselt toimetada SISU MUUTMATA.
Kõik kontrollid on deterministlikud:
  - parandus: oodatud õige vorm on olemas ja vale vorm on kadunud
  - kaitstud: nimed, kuupäevad, numbrid ja ID-d on alles täpselt samal kujul
  - häirekell: oleku-, eitus- ja ebakindlussõnade arv on sama mis allikas (näide: „kaalub kinnitamist“ → „kinnitas“)
  - omistus: nimi ja tema tegevus jäävad samasse järjekorda (nimi enne tegusõna tüve)
  - puhas plokk: vastus täpselt muutmata; muutunud sõnade osakaal on diagnostika
  - üle-toimetamine (olek/omistus): muutunud sõnade osakaal ≤ max_muutus; raport näitab, kui kukkus ainult selle piiri tõttu
Häirekell on häire, mitte tõend. Raport loeb eraldi kokku, mitu korda lükkas häirekell tagasi sisuliselt korrektse paranduse (käsitsi ülevaatus).
"""
import re
import difflib
from typing import Any, Dict, List

# Oleku-, eitus- ja ebakindlussõnade tüved (suletud hulk). Võrreldakse sõna algust, väiketähtedega.
OLEK_TUVED = ["otsust", "otsusta", "kinnit", "kaalu", "arut", "tühist", "lükka", "lükk", "ettepanek", "paku", "pakku"]
EITUS = {"ei", "pole", "mitte", "ära", "ega"}
EBAKINDLUS_TUVED = ["võib-olla", "võibolla", "ilmselt", "vist", "tõenäoliselt", "kindel", "kindla", "kindlalt", "äkki", "arvatavasti"]

PREFIKSID = re.compile(r"^\s*(toimetatud tekst|parandatud tekst|tekst|vastus)\s*:\s*", re.IGNORECASE)


def puhasta(output: str) -> str:
    t = re.sub(r"<think>.*?</think>", "", output or "", flags=re.DOTALL).strip()
    t = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", t).strip()
    t = PREFIKSID.sub("", t).strip()
    if len(t) >= 2 and t[0] in "\"„“'" and t[-1] in "\"“”'":
        t = t[1:-1].strip()
    return t


def sonad(t: str) -> List[str]:
    return re.findall(r"[\wäöüõšžÄÖÜÕŠŽ'’.-]+", t.lower())


def _loe(t: str) -> Dict[str, int]:
    w = [x.strip(".,;:!?") for x in sonad(t)]
    return {
        "olek": sum(1 for x in w if any(x.startswith(s) for s in OLEK_TUVED)),
        "eitus": sum(1 for x in w if x in EITUS),
        "ebakindlus": sum(1 for x in w if any(x.startswith(s) for s in EBAKINDLUS_TUVED)),
    }


def _sisaldab(t: str, fraas: str) -> bool:
    return fraas.lower() in t.lower()


def _muutus(a: str, b: str) -> float:
    wa, wb = sonad(a), sonad(b)
    if not wa:
        return 0.0 if not wb else 1.0
    return round(1.0 - difflib.SequenceMatcher(None, wa, wb).ratio(), 3)


def _omistus_korras(t: str, nimi: str, tuvi: str) -> bool:
    low = t.lower()
    for lause in re.split(r"(?<=[.!?;])\s+|,\s+", low):
        i = lause.find(nimi.lower())
        if i < 0:
            continue
        rest = lause[i + len(nimi):]
        if re.search(r"\b" + re.escape(tuvi.lower()), rest):
            return True
    return False


def evaluate_edit(test: Dict[str, Any], output: str) -> Dict[str, Any]:
    e = test["expected"]
    allikas = test["allikas"]
    t = puhasta(output)
    k: Dict[str, Any] = {}

    if not t:
        return {"passed": False, "kontrollid": {"tühi_vastus": False}, "häirekell": None, "muutus": None, "tekst": t}

    # element võib olla string või alternatiivide loend (one_of)
    k["peab_sisaldama"] = all(
        any(_sisaldab(t, x) for x in (f if isinstance(f, list) else [f])) for f in e.get("peab_sisaldama", [])
    )
    k["ei_tohi_sisaldada"] = not any(_sisaldab(t, f) for f in e.get("ei_tohi_sisaldada", []))
    k["kaitstud"] = all(f in t for f in e.get("kaitstud", []))
    a, b = _loe(allikas), _loe(t)
    k["häirekell_vaikne"] = (a == b)
    if e.get("omistus"):
        k["omistus"] = all(_omistus_korras(t, n, s) for n, s in e["omistus"])
    muutus = _muutus(allikas, t)
    if e.get("tapne"):
        # puhas plokk: vastus peab olema muutmata (lubatud ainult servatühikud ja reavahetuste/tühikute ühtlustus)
        k["muutmata"] = re.sub(r"\s+", " ", t).strip() == re.sub(r"\s+", " ", allikas).strip()
    if "max_muutus" in e:
        k["üle_toimetamine_puudub"] = muutus <= e["max_muutus"]
    # ainult üks lõik, mitte selgitus juurde
    k["ainult_tekst"] = len(t) <= max(2 * len(allikas), len(allikas) + 120)

    return {
        "passed": all(bool(v) for v in k.values()),
        "kontrollid": k,
        "häirekell": {"allikas": a, "vastus": b},
        "muutus": muutus,
        "tekst": t,
    }
