#!/usr/bin/env python3
"""Generate Spanish TTS podcasts from markdown temas using macOS 'say'.

Cleans markdown so the TTS doesn't read symbols (#, *, |, etc.) and
expands common abbreviations / acronyms so the voice pronounces them
naturally.
"""
import re
import subprocess
from pathlib import Path

TEMARIO = Path(__file__).parent.parent / "temario"
OUT = Path(__file__).parent
OUT.mkdir(exist_ok=True)

# Acronyms and abbreviations to expand for natural pronunciation
EXPANSIONS = {
    # Renfe-specific
    "CCGGT": "Condiciones Generales de Transporte",
    "OSP": "Obligaciones de Servicio Público",
    "AVE": "A V E",
    "AVLO": "Avlo",
    "FIP": "F I P",
    "UIC": "U I C",
    "PMR": "personas con movilidad reducida",
    "SGS": "Sistema de Gestión de Seguridad",
    "RFIG": "Red Ferroviaria de Interés General",
    "ADIF": "Adif",
    "ADIF-AV": "Adif Alta Velocidad",
    "AESF": "A E S F",
    "CNMC": "C N M C",
    "CIAF": "C I A F",
    "EUAR": "E U A R",
    "ERA": "E R A",
    "ETCS": "E T C S",
    "ERTMS": "E R T M S",
    "ASFA": "Asfa",
    "LZB": "L Z B",
    "DMI": "D M I",
    "GSM-R": "GSM Erre",
    "CTC": "C T C",
    "ETI": "E T I",
    "LOIEMH": "Ley Orgánica para la Igualdad Efectiva de Mujeres y Hombres",
    "RGPD": "Reglamento General de Protección de Datos",
    "LOPDGDD": "Ley Orgánica de Protección de Datos",
    "CX": "experiencia de cliente",
    "UX": "experiencia de usuario",
    "VoC": "voz del cliente",
    "NPS": "N P S",
    "CES": "C E S",
    "CSAT": "C SAT",
    "KPI": "K P I",
    "KPIs": "K P I s",
    "IA": "inteligencia artificial",
    "FRMCS": "F R M C S",
    "MD": "Media Distancia",
    "LD": "Larga Distancia",
    "RRHH": "Recursos Humanos",
    "PRL": "Prevención de Riesgos Laborales",
    "CC.OO.": "Comisiones Obreras",
    "U.G.T.": "U G T",
    "S.E.M.A.F.": "S E M A F",
    "AGE": "Administración General del Estado",
    "BOE": "B O E",
    "DNI": "D N I",
    "VCX": "V C X",
    "VOLP": "V O L P",
    "VOLA": "V O L A",
    "VAV": "V A V",
    "VAP/VAN": "V A P, V A N",
    "VMR": "V M R",
    "VTE": "V T E",
    "ARES": "Ares",
    "FV": "F V",
    "RBC": "R B C",
    "FCR": "F C R",
    "CAF": "C A F",
    "SNCF": "S N C F",
    "DB": "D B",
    "ÖBB": "O B B",
    "SBB/CFF": "S B B",
    "NS": "N S",
    "SNCB": "S N C B",
    "CD": "C D",
    "PKP": "P K P",
    "MAV": "M A V",
    "FS": "F S",
    "CP": "C P",
    "FEVE": "Feve",
    "MZA": "M Z A",
    "AV": "Alta Velocidad",
    "LSF": "Ley del Sector Ferroviario",
}


def clean_markdown(text: str) -> str:
    """Strip markdown formatting and prepare text for natural TTS."""
    # Remove blockquote markers
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Strip headers (# ## ###) but keep the text
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

    # Remove markdown bold/italic markers
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove inline code backticks
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Remove emoji and special icons commonly used
    text = re.sub(r"[🚆⚖️🦺💛🚂📑📚📅🧪🔥📝📸🎯⭐⚠️🟦🟧🟩🟠🟡🔴📁🧭💡✅❌📌📊🔑🗺️]", "", text)

    # Convert tables to readable prose
    lines = text.split("\n")
    cleaned = []
    in_table = False
    for line in lines:
        if "|" in line and line.strip().startswith("|"):
            # Skip separator rows like |---|---|
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                continue
            # Table row -> read cells with pauses
            cells = [c.strip() for c in line.split("|")[1:-1]]
            cells = [c for c in cells if c]
            cleaned.append(". ".join(cells) + ".")
            in_table = True
        else:
            if in_table and line.strip() == "":
                in_table = False
            cleaned.append(line)
    text = "\n".join(cleaned)

    # Remove markdown links: [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove bullet markers
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)

    # Expand acronyms (longest first to avoid partial matches)
    for acr in sorted(EXPANSIONS.keys(), key=len, reverse=True):
        # Use word boundaries when possible
        pattern = r"\b" + re.escape(acr) + r"\b"
        text = re.sub(pattern, EXPANSIONS[acr], text)

    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leftover special chars that confuse TTS
    text = text.replace("&", " y ")
    text = text.replace("→", " a ")
    text = text.replace("≥", " mayor o igual que ")
    text = text.replace("≤", " menor o igual que ")
    text = text.replace("⊂", "")
    text = text.replace("~", "aproximadamente ")
    text = text.replace("€", " euros")
    text = text.replace("%", " por ciento")

    return text.strip()


def generate_podcast(md_path: Path, out_path: Path, voice: str = "Monica", rate: int = 200):
    """Generate an m4a audio file from the markdown."""
    raw = md_path.read_text()
    clean = clean_markdown(raw)

    # Write cleaned text to a temp file (say can read from file)
    txt_path = out_path.with_suffix(".txt")
    txt_path.write_text(clean)

    aiff_path = out_path.with_suffix(".aiff")
    print(f"Generating {out_path.name}...", flush=True)

    # say -v Monica -r 200 -f input.txt -o output.aiff
    subprocess.run(
        ["say", "-v", voice, "-r", str(rate), "-f", str(txt_path), "-o", str(aiff_path)],
        check=True,
    )

    # Convert aiff to m4a for smaller file size
    m4a_path = out_path.with_suffix(".m4a")
    subprocess.run(
        ["afconvert", str(aiff_path), str(m4a_path), "-f", "m4af", "-d", "aac"],
        check=True,
    )

    # Cleanup aiff (keep txt for reference)
    aiff_path.unlink()
    print(f"  → {m4a_path.name} ({m4a_path.stat().st_size / 1024 / 1024:.1f} MB)", flush=True)


def main():
    temas = sorted(TEMARIO.glob("tema-*.md"))
    print(f"Found {len(temas)} temas. Generating podcasts with voice 'Monica' (es_ES) at 200 wpm...\n")

    for md in temas:
        out = OUT / md.stem
        generate_podcast(md, out)

    print("\n✅ Done. Podcasts ready in:", OUT)


if __name__ == "__main__":
    main()
