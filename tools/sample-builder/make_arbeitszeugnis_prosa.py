# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "pyyaml", "pillow"]
# ///
"""Generate a qualifiziertes Arbeitszeugnis: the standard German prose
employer reference letter (modeled on the arbeitsrechte.de Muster in
samples/). Deliberately states the employment period and duties but NEVER
weekly hours or full-time/part-time status — the typical real-world gap that
makes the 32 h/week full-time test (L766) unevidenceable from this document
alone. Output:

  samples/filled-documents/<slug>/arbeitszeugnis.pdf        (+ -scan.pdf)

Usage: uv run tools/sample-builder/make_arbeitszeugnis_prosa.py samples/filled-documents/tobias-renner/tobias-renner.yaml
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
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
    c = canvas.Canvas(str(path), pagesize=A4)
    # Letterhead
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, H - 70, d["firma"])
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, H - 84, d["firma_adresse"])
    c.setLineWidth(0.8)
    c.line(MARGIN, H - 94, W - MARGIN, H - 94)

    c.setFont("Times-Bold", 14)
    c.drawCentredString(W / 2, H - 140, "Arbeitszeugnis")

    y = H - 180
    y = para(
        c,
        f"{d['anrede']} {d['name']}, geboren am {d['birth_date']} in "
        f"{d['birth_place']}, war vom {d['vom']} bis zum {d['bis']} als "
        f"{d['position']} in unserem Unternehmen beschäftigt.",
        y,
    )
    y = para(c, d["firma_beschreibung"], y - 8)
    y = para(
        c,
        f"Das Aufgabengebiet von {d['anrede']} {d['nachname']} umfasste im "
        f"Einzelnen die folgenden Tätigkeiten:",
        y - 8,
    )
    y -= 4
    c.setFont(FONT, 11)
    for task in d["aufgaben"]:
        for i, line in enumerate(simpleSplit(task, FONT, 11, TEXT_W - 20)):
            c.drawString(MARGIN + 12, y, ("•  " if i == 0 else "    ") + line)
            y -= 16
    y -= 8
    for absatz in d["beurteilung"]:
        y = para(c, absatz, y)
        y -= 8
    y = para(
        c,
        f"{d['anrede']} {d['nachname']} verlässt unser Unternehmen auf eigenen "
        f"Wunsch. Wir danken {d['dank_pronomen']} für die stets sehr gute "
        f"Zusammenarbeit und wünschen {d['dank_pronomen']} für den weiteren "
        f"Berufs- und Lebensweg alles Gute und viel Erfolg.",
        y,
    )

    y -= 40
    c.setFont(FONT, 11)
    c.drawString(MARGIN, y, d["ort_datum"])
    y -= 50
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(MARGIN, y, d["unterzeichner"])
    c.setLineWidth(0.6)
    c.line(MARGIN, y - 4, MARGIN + 160, y - 4)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y - 16, d["unterzeichner_titel"])
    c.drawString(MARGIN, y - 28, d["firma"])
    c.save()


def rasterize(pdf_path, out_path, dpi=150):
    """Simulate an uploaded scan: rasterize and re-wrap as PDF."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), f"{td}/p"],
            check=True,
        )
        pages = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("p*.png"))]
        pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=dpi)


def main():
    d = yaml.safe_load(Path(sys.argv[1]).read_text())
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / d["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "arbeitszeugnis.pdf"
    build(d, out)
    rasterize(out, out_dir / "arbeitszeugnis-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
