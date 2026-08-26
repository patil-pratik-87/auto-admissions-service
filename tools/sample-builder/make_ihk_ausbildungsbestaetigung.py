# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "pyyaml"]
# ///
"""Generate an IHK Bestätigung über das Berufsausbildungsverhältnis: the
confirmation letter an IHK issues from its Verzeichnis der
Berufsausbildungsverhältnisse (§ 34 BBiG). Unlike the Prüfungszeugnis, this
document explicitly states the training contract period and duration in
months — the evidence the professional-access duration gate needs. Output:

  samples/filled-documents/<slug>/ihk-ausbildungsbestaetigung.pdf

Usage: uv run tools/sample-builder/make_ihk_ausbildungsbestaetigung.py samples/filled-documents/tobias-falk/tobias-falk.yaml
"""

import sys
from pathlib import Path

import yaml
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

W, H = A4
MARGIN = 75.0
TEXT_W = W - 2 * MARGIN
FONT = "Times-Roman"


def para(c, text, y, size=11, leading=16):
    c.setFont(FONT, size)
    for line in simpleSplit(text, FONT, size, TEXT_W):
        c.drawString(MARGIN, y, line)
        y -= leading
    return y


def build(d, path):
    a = d["ausbildungsbestaetigung"]
    i = d["ihk"]
    c = canvas.Canvas(str(path), pagesize=A4)
    # Letterhead (same chamber as the Prüfungszeugnis specimen)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, H - 70, "Industrie- und Handelskammer Nord Westfalen")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, H - 84, "Sentmaringer Weg 61 · 48151 Münster")
    c.setLineWidth(0.8)
    c.line(MARGIN, H - 94, W - MARGIN, H - 94)

    c.setFont("Times-Bold", 14)
    c.drawCentredString(W / 2, H - 150, "Bestätigung über das Berufsausbildungsverhältnis")

    y = H - 195
    y = para(
        c,
        f"Die Industrie- und Handelskammer Nord Westfalen bestätigt, dass "
        f"{a['anrede']} {d['name']}, geboren am {i['geburtsdatum_lang']}, mit dem "
        f"nachstehenden Berufsausbildungsverhältnis in das Verzeichnis der "
        f"Berufsausbildungsverhältnisse (§ 34 BBiG) eingetragen war:",
        y,
    )
    y -= 12
    rows = [
        ("Ausbildungsberuf:", a["beruf"]),
        ("Ausbildungsbetrieb:", a["betrieb"]),
        ("Beginn der Ausbildung:", a["beginn"]),
        ("Ende der Ausbildung:", a["ende"]),
        ("Ausbildungsdauer:", a["dauer"]),
        ("Abschlussprüfung bestanden am:", a["pruefung_bestanden_am"]),
    ]
    for label, value in rows:
        c.setFont("Times-Bold", 11)
        c.drawString(MARGIN, y, label)
        c.setFont(FONT, 11)
        c.drawString(MARGIN + 200, y, value)
        y -= 18
    y -= 12
    y = para(
        c,
        "Diese Bestätigung wird auf Antrag zur Vorlage bei Behörden und "
        "Bildungseinrichtungen ausgestellt.",
        y,
    )

    y -= 40
    c.setFont(FONT, 11)
    c.drawString(MARGIN, y, f"Münster, {a['datum']}")
    y -= 50
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(MARGIN, y, i["hauptgeschaeftsfuehrer"])
    c.setLineWidth(0.6)
    c.line(MARGIN, y - 4, MARGIN + 160, y - 4)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y - 16, "Hauptgeschäftsführer")
    c.drawString(MARGIN, y - 28, "Industrie- und Handelskammer Nord Westfalen")
    c.save()


def main():
    d = yaml.safe_load(Path(sys.argv[1]).read_text())
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / d["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "ihk-ausbildungsbestaetigung.pdf"
    build(d, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
