# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "reportlab", "pyyaml", "pillow"]
# ///
"""Fill the IHK Pruefungszeugnis specimen (samples/blank-documents/ihk-musterzeugnis.pdf,
IHK Nord Westfalen, Kaufmann fuer Bueromanagement) with synthetic applicant
data.

Unlike the blank KMK templates this is a *filled* Muster, so the personal
lines (name, birth date, issue date, signatory names) are whited out and
rewritten; occupation, grades, and the printed DQR Niveau 4 line stay as
printed so the document remains internally consistent. Output:

  samples/filled-documents/<slug>/ihk-zeugnis.pdf        vector-filled
  samples/filled-documents/<slug>/ihk-zeugnis-scan.pdf   150dpi raster ("scan")

Usage: uv run tools/sample-builder/fill_ihk_zeugnis.py samples/filled-documents/daniel-roth/daniel-roth.yaml
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

TEMPLATE = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "ihk-musterzeugnis.pdf"
PAGE_H = 841.89

# Known limitation: patch() hides the Muster's specimen data (Max Mustermann,
# birth date, signatories, serial) only visually — it survives in the vector
# PDF's text layer. The -scan.pdf variants are the pipeline's only extraction
# input, so this is deliberate; see docs/OPEN-QUESTIONS.md #5 before ever
# feeding the vector PDFs to a text-based extractor.


def patch(c, x0, top, bottom, x1, text, x, size, font="Helvetica", offset=None):
    """White-out the rect (x0..x1, top..bottom) and write `text` at x on the
    original baseline (top + ~0.8*size unless overridden)."""
    c.setFillColorRGB(1, 1, 1)
    c.rect(x0, PAGE_H - bottom, x1 - x0, bottom - top, stroke=0, fill=1)
    c.setFillColorRGB(0.13, 0.13, 0.13)
    c.setFont(font, size)
    c.drawString(x, PAGE_H - top - (offset if offset else size * 0.8), text)


def page0_overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595.28, PAGE_H))
    i = d["ihk"]
    # Name line ("Max Mustermann", bold 20pt at top 228.1). ihk.name overrides
    # for personas whose top-level name uses the KMK "Nachname, Vorname" form.
    patch(c, 72, 226, 250, 450, i.get("name", d["name"]), 73.7, 20, font="Helvetica-Bold")
    # Birth date inside "geboren am <date> hat die Abschlusspruefung"
    patch(c, 126.5, 256, 271, 207.5, i["geburtsdatum_lang"], 127.9, 11, offset=9)
    # Occupation title is printed "Kaufmann ..." - regender for female personas
    if i.get("kauffrau"):
        patch(c, 74.5, 298, 320, 141, "Kauffrau", 74.8, 16, font="Helvetica-Bold")
    # Issue line "Muenster, 21. Juni 2023"
    patch(c, 72, 677, 691, 260, f"Münster, {i['datum']}", 73.7, 9, offset=7.5)
    # Signatory names (the Muster carries real IHK officials - replace)
    patch(c, 72, 780, 795, 450, i["praesident"], 73.7, 9, offset=7.5)
    c.drawString(343.0, PAGE_H - 782.9 - 7.5, i["hauptgeschaeftsfuehrer"])
    c.save()
    buf.seek(0)
    return buf


def page1_overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595.28, PAGE_H))
    i = d["ihk"]
    patch(c, 72, 228, 253, 450, i.get("name", d["name"]), 74.3, 20, font="Helvetica-Bold")
    patch(c, 126, 256, 271, 207.5, i["geburtsdatum_lang"], 127.4, 11, offset=9)
    if i.get("kauffrau"):
        patch(c, 74.8, 298, 320, 141.3, "Kauffrau", 75.1, 16, font="Helvetica-Bold")
    c.save()
    buf.seek(0)
    return buf


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
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / data["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    template = PdfReader(TEMPLATE)
    writer = PdfWriter()
    for idx, overlay in ((0, page0_overlay(data)), (1, page1_overlay(data))):
        page = template.pages[idx]
        page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(page)

    out = out_dir / "ihk-zeugnis.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    rasterize(out, out_dir / "ihk-zeugnis-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
