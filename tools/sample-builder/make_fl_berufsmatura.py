# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "pyyaml", "pillow"]
# ///
"""Generate a synthetic Liechtenstein Berufsmaturitaetszeugnis: a
German-language, subject-restricted higher-education entrance qualification
whose issuing state (Fuerstentum Liechtenstein) is clearly stated and lies
OUTSIDE the DACH set (Germany, Austria, Switzerland) used by the fact
builder. The German-language layout deliberately tests that issuing_region
is derived from the stated country, not from the document language. Output:

  samples/filled-documents/<slug>/berufsmaturitaetszeugnis.pdf        (+ -scan.pdf)

Usage: uv run tools/sample-builder/make_fl_berufsmatura.py samples/filled-documents/<slug>/<slug>.yaml
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

W, H = A4
MARGIN = 80.0


def build(d, path):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W / 2, H - 75, "FÜRSTENTUM LIECHTENSTEIN")
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, H - 90, d["schule"])
    c.setLineWidth(0.8)
    c.line(MARGIN, H - 104, W - MARGIN, H - 104)

    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(W / 2, H - 150, "Berufsmaturitätszeugnis")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H - 170, d["richtung"])

    y = H - 215
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, y, f"{d['name']}, geboren am {d['birth_date']} in {d['birth_place']},")
    y -= 18
    c.drawCentredString(W / 2, y, "hat die Berufsmaturitätsprüfung bestanden.")

    # Fächer table, Swiss grade scale (6 = best, 4 = pass threshold).
    y -= 45
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 40, y, "Fach")
    c.drawRightString(W - MARGIN - 40, y, "Note")
    c.setLineWidth(0.5)
    c.line(MARGIN + 40, y - 5, W - MARGIN - 40, y - 5)
    y -= 22
    c.setFont("Helvetica", 10)
    for fach, note in d["faecher"]:
        c.drawString(MARGIN + 40, y, fach)
        c.drawRightString(W - MARGIN - 40, y, note)
        y -= 16
    y -= 8
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 40, y, "Gesamtnote")
    c.drawRightString(W - MARGIN - 40, y, d["gesamtnote"])

    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, y, "Dieses Zeugnis berechtigt zur Aufnahme eines Studiums in den der")
    c.drawString(MARGIN, y - 13, "Ausbildungsrichtung entsprechenden Studiengängen.")

    y -= 60
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, y, d["ort_datum"])
    y -= 50
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(MARGIN, y, d["schulleitung"])
    c.drawString(W / 2 + 20, y, d["amt"])
    c.setLineWidth(0.6)
    c.line(MARGIN, y - 4, MARGIN + 150, y - 4)
    c.line(W / 2 + 20, y - 4, W / 2 + 170, y - 4)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y - 16, "Schulleitung")
    c.drawString(W / 2 + 20, y - 16, "Amt für Berufsbildung und Berufsberatung")
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
    out = out_dir / "berufsmaturitaetszeugnis.pdf"
    build(d, out)
    rasterize(out, out_dir / "berufsmaturitaetszeugnis-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
