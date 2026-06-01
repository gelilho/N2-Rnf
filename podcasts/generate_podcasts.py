#!/usr/bin/env python3
"""Generate Spanish TTS podcasts from markdown temas using Microsoft Edge Neural TTS.

Uses 'edge-tts' (free, no API key) with neural Spanish voice.
Cleans markdown so the TTS doesn't read symbols and expands acronyms
so the voice pronounces them naturally with proper pauses.
"""
import asyncio
import re
import subprocess
from pathlib import Path

import edge_tts

TEMARIO = Path(__file__).parent.parent / "temario"
OUT = Path(__file__).parent
OUT.mkdir(exist_ok=True)

# Spanish (Spain) neural voice — Elvira is neutral, clear, news-style
VOICE = "es-ES-ElviraNeural"

# Speaking rate: -10% slower than default for study comfort
RATE = "-5%"

# Acronyms and abbreviations to expand or spell out
EXPANSIONS = {
    "CCGGT": "Condiciones Generales de Transporte",
    "OSP": "O. S. P.",
    "AVE": "A. V. E.",
    "AVLO": "Avlo",
    "FIP": "F. I. P.",
    "UIC": "U. I. C.",
    "PMR": "personas con movilidad reducida",
    "SGS": "Sistema de Gestión de Seguridad",
    "RFIG": "Red Ferroviaria de Interés General",
    "ADIF": "Adif",
    "ADIF-AV": "Adif Alta Velocidad",
    "AESF": "A. E. S. F.",
    "CNMC": "C. N. M. C.",
    "CIAF": "C. I. A. F.",
    "EUAR": "E. U. A. R.",
    "ERA": "E. R. A.",
    "ETCS": "E. T. C. S.",
    "ERTMS": "E. R. T. M. S.",
    "ASFA": "Asfa",
    "LZB": "L. Z. B.",
    "DMI": "D. M. I.",
    "GSM-R": "G. S. M. erre",
    "CTC": "C. T. C.",
    "ETI": "E. T. I.",
    "LOIEMH": "Ley Orgánica para la Igualdad Efectiva de Mujeres y Hombres",
    "RGPD": "R. G. P. D.",
    "LOPDGDD": "L. O. P. D.",
    "CX": "C. X.",
    "UX": "U. X.",
    "VoC": "voz del cliente",
    "NPS": "N. P. S.",
    "CES": "C. E. S.",
    "CSAT": "C. SAT",
    "KPI": "K. P. I.",
    "KPIs": "K. P. I. s",
    "IA": "inteligencia artificial",
    "FRMCS": "F. R. M. C. S.",
    "MD": "Media Distancia",
    "LD": "Larga Distancia",
    "RRHH": "Recursos Humanos",
    "PRL": "P. R. L.",
    "CC.OO.": "Comisiones Obreras",
    "U.G.T.": "U. G. T.",
    "S.E.M.A.F.": "S. E. M. A. F.",
    "AGE": "Administración General del Estado",
    "BOE": "B. O. E.",
    "DNI": "D. N. I.",
    "VCX": "V. C. X.",
    "VOLP": "V. O. L. P.",
    "VOLA": "V. O. L. A.",
    "VAV": "V. A. V.",
    "VAP/VAN": "V. A. P. y V. A. N.",
    "VMR": "V. M. R.",
    "VTE": "V. T. E.",
    "ARES": "Ares",
    "FV": "F. V.",
    "RBC": "R. B. C.",
    "FCR": "F. C. R.",
    "CAF": "C. A. F.",
    "SNCF": "S. N. C. F.",
    "DB": "D. B.",
    "ÖBB": "Ö. B. B.",
    "SBB/CFF": "S. B. B.",
    "NS": "N. S.",
    "SNCB": "S. N. C. B.",
    "CD": "C. D.",
    "PKP": "P. K. P.",
    "MAV": "M. A. V.",
    "FS": "F. S.",
    "CP": "C. P.",
    "FEVE": "Feve",
    "MZA": "M. Z. A.",
    "AV": "Alta Velocidad",
    "LSF": "Ley del Sector Ferroviario",
}


def clean_markdown(text: str) -> str:
    """Strip markdown formatting and prepare text for natural TTS."""
    # Blockquote markers
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Headers (#) -> add period for pause
    def header_to_pause(m):
        content = m.group(2).strip()
        # Remove emoji-like leading chars
        content = re.sub(r"^[^\w]+", "", content)
        return f"\n\n{content}.\n\n"
    text = re.sub(r"^(#+)\s*(.+)$", header_to_pause, text, flags=re.MULTILINE)

    # Bold/italic markers
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Emoji and icons
    text = re.sub(r"[🚆⚖️🦺💛🚂📑📚📅🧪🔥📝📸🎯⭐⚠️🟦🟧🟩🟠🟡🔴📁🧭💡✅❌📌📊🔑🗺️🇪🇸🇫🇷🇩🇪🇮🇹📍🎧🎙️]", "", text)

    # Convert tables to readable prose
    lines = text.split("\n")
    cleaned = []
    in_table = False
    for line in lines:
        if "|" in line and line.strip().startswith("|"):
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            cells = [c for c in cells if c]
            if cells:
                # Use ", " as separator + period at end for clear pauses
                cleaned.append(", ".join(cells) + ".")
            in_table = True
        else:
            if in_table and line.strip() == "":
                in_table = False
            cleaned.append(line)
    text = "\n".join(cleaned)

    # Markdown links
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Bullets and numbered lists -> period for natural pause
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

    # Horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)

    # Expand acronyms (longest first)
    for acr in sorted(EXPANSIONS.keys(), key=len, reverse=True):
        pattern = r"\b" + re.escape(acr) + r"\b"
        text = re.sub(pattern, EXPANSIONS[acr], text)

    # Special chars
    text = text.replace("&", " y ")
    text = text.replace("→", ", ")
    text = text.replace("≥", " mayor o igual que ")
    text = text.replace("≤", " menor o igual que ")
    text = text.replace("~", "aproximadamente ")
    text = text.replace("€", " euros")
    text = text.replace("%", " por ciento")
    text = text.replace("…", ".")

    # Collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    # Ensure proper sentence endings
    text = re.sub(r"\n+", "\n\n", text)

    return text.strip()


async def synth(text: str, mp3_path: Path):
    """Generate MP3 directly via edge-tts."""
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(str(mp3_path))


def generate_podcast(md_path: Path, out_path: Path):
    raw = md_path.read_text()
    clean = clean_markdown(raw)

    mp3_path = out_path.with_suffix(".mp3")
    print(f"Generating {mp3_path.name}...", flush=True)
    asyncio.run(synth(clean, mp3_path))
    print(f"  → {mp3_path.name} ({mp3_path.stat().st_size / 1024 / 1024:.1f} MB)", flush=True)


def main():
    temas = sorted(TEMARIO.glob("tema-*.md"))
    print(f"Found {len(temas)} temas. Generating podcasts with {VOICE} at rate {RATE}...\n")
    for md in temas:
        out = OUT / md.stem
        generate_podcast(md, out)
    print("\nDone. Podcasts in:", OUT)


if __name__ == "__main__":
    main()
