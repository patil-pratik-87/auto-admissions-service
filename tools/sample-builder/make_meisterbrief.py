# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "pyyaml", "pillow"]
# ///
"""Generate a decorative Meisterbrief (Schmuckurkunde) — the ornamental
wall-hanging certificate a Handwerkskammer issues alongside the graded
Pruefungszeugnis. Deliberately carries NO DQR level line and NO
exam-regulation citation: name, trade, chamber, date, signatures only.
A bundle containing only this document must not pass the B2 DQR-6 check
silently (FORTBILDUNG_ROUTE_REVIEW).

Output:

  samples/filled-documents/<slug>/meisterbrief.pdf        vector
  samples/filled-documents/<slug>/meisterbrief-scan.pdf   150dpi raster ("scan")

Usage: uv run tools/sample-builder/make_meisterbrief.py samples/filled-documents/<slug>/<slug>.yaml
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = landscape(A4)  # 842.04 x 595.32


def draw_border(c):
    c.setLineWidth(3)
    c.rect(30, 30, PAGE_W - 60, PAGE_H - 60)
    c.setLineWidth(0.8)
    c.rect(38, 38, PAGE_W - 76, PAGE_H - 76)
    c.rect(44, 44, PAGE_W - 88, PAGE_H - 88)
    # corner ornaments: small diamonds inside the inner frame
    for x in (60, PAGE_W - 60):
        for y in (60, PAGE_H - 60):
            c.saveState()
            c.translate(x, y)
            c.rotate(45)
            c.rect(-5, -5, 10, 10, stroke=1, fill=0)
            c.restoreState()


def make(d):
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / d["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "meisterbrief.pdf"

    c = canvas.Canvas(str(out), pagesize=(PAGE_W, PAGE_H))
    draw_border(c)
    cx = PAGE_W / 2

    c.setFont("Times-Roman", 14)
    c.drawCentredString(cx, 500, d["chamber"])
    c.setFont("Times-Bold", 40)
    c.drawCentredString(cx, 440, "Meisterbrief")
    c.setLineWidth(0.8)
    c.line(cx - 110, 428, cx + 110, 428)

    c.setFont("Times-Roman", 13)
    c.drawCentredString(cx, 388, "Die Handwerkskammer verleiht")
    c.setFont("Times-Bold", 22)
    c.drawCentredString(cx, 352, d["name"])
    c.setFont("Times-Roman", 13)
    c.drawCentredString(cx, 324, f"geboren am {d['birth_date']} in {d['birth_place']},")
    c.drawCentredString(cx, 296, "auf Grund der bestandenen Meisterprüfung die Befugnis,")
    c.setFont("Times-Italic", 16)
    c.drawCentredString(cx, 262, f"den Titel {d['title']} zu führen")
    c.setFont("Times-Roman", 13)
    c.drawCentredString(cx, 234, "und Lehrlinge auszubilden.")

    c.setFont("Times-Roman", 12)
    c.drawCentredString(cx, 175, d["ort_datum"])

    c.setFont("Times-Italic", 12)
    c.drawCentredString(cx - 200, 120, d["praesident"])
    c.drawCentredString(cx + 200, 120, d["geschaeftsfuehrer"])
    c.setLineWidth(0.5)
    c.line(cx - 290, 112, cx - 110, 112)
    c.line(cx + 110, 112, cx + 290, 112)
    c.setFont("Times-Roman", 10)
    c.drawCentredString(cx - 200, 98, "Der Präsident")
    c.drawCentredString(cx + 200, 98, "Der Geschäftsführer")
    c.save()
    return out, out_dir


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
    data = yaml.safe_load(Path(sys.argv[1]).read_text())
    out, out_dir = make(data)
    rasterize(out, out_dir / "meisterbrief-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
