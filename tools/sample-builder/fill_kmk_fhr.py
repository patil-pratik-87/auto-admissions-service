# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "reportlab", "pyyaml", "pillow"]
# ///
"""Fill the KMK 'Bescheinigung ueber den schulischen Teil der Fachhochschulreife'
template (samples/blank-documents/kmk-fhr.pdf) with synthetic applicant data.

The template has no AcroForm fields, so text is overlaid at hard-coded
coordinates measured from the original PDF (pdfplumber). Output:

  samples/filled-documents/<slug>/kmk-fhr-schulischer-teil.pdf        vector-filled
  samples/filled-documents/<slug>/kmk-fhr-schulischer-teil-scan.pdf   150dpi raster ("scan")

Usage: uv run tools/sample-builder/fill_kmk_fhr.py samples/filled-documents/max-mustermann/max-mustermann.yaml
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

TEMPLATE = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "kmk-fhr.pdf"
PAGE_H = 841.92  # template page height in points; overlay y = PAGE_H - top

# Template page indices: 2 = certificate page ("-3-"), 3 = grades page ("-4a-",
# Gymnasiale Oberstufe variant).
CERT_PAGE, GRADES_PAGE = 2, 3


def draw(c, x, top, text, size=11, font="Helvetica", center=False):
    c.setFont(font, size)
    y = PAGE_H - top - 9.5  # baseline sits on the printed underscore/cell line
    if center:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


def cert_overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595.32, PAGE_H))
    draw(c, 297.7, 155.0, d["school"], center=True)
    draw(c, 200.0, 245.0, d["name"])
    draw(c, 130.0, 278.0, d["birth_date"])
    draw(c, 310.0, 278.0, d["birth_place"])
    draw(c, 150.0, 311.0, d["address"])
    draw(c, 100.0, 377.5, d["school_type_insert"])
    draw(c, 128.0, 410.5, d["halbjahr_1"], center=True)
    draw(c, 231.0, 410.5, d["halbjahr_2"], center=True)
    # Durchschnittsnote box: left cell x 187.8-258.8, right cell 258.8-407.7,
    # cells span top 538.0-552.4. Optional: omit to produce an ABSENT-field
    # specimen (extraction should yield status ABSENT, not a guess).
    if d.get("durchschnittsnote_ziffer"):
        draw(c, 223.0, 540.0, d["durchschnittsnote_ziffer"], size=10, center=True)
        draw(c, 333.0, 540.0, d["durchschnittsnote_text"], size=10, center=True)
    c.save()
    buf.seek(0)
    return buf


# Grades page geometry: subject rows share these tops; height ~12.7pt each.
ROW_TOPS = [249.0, 261.7, 274.8, 288.0, 301.1]


def grades_overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595.32, PAGE_H))
    draw(c, 200.0, 132.0, d["name"])
    # Table I (einfache Wertung): Fach 70.7-148.7 | Zahl 148.7-226.7 |
    # Bewertung subcells 226.7-269.2 / 269.2-311.7 (grade in right subcell)
    for row, (fach, zahl, punkte) in zip(ROW_TOPS, d["subjects_einfach"]):
        draw(c, 75.0, row + 1.5, fach, size=9)
        draw(c, 187.7, row + 1.5, zahl, size=9, center=True)
        draw(c, 290.5, row + 1.5, punkte, size=9, center=True)
    # Table II (zweifache Wertung): Fach 343.8-450.1 | grade subcell 490.8-531.4
    for row, (fach, punkte) in zip(ROW_TOPS[:4], d["subjects_zweifach"]):
        draw(c, 348.0, row + 1.5, fach, size=9)
        draw(c, 511.0, row + 1.5, punkte, size=9, center=True)
    # Punktsumme boxes (gray cells): I at x 269.7-311.7 top 314.8-340.1,
    # II at x 491.2-531.4 top 301.7-340.1
    draw(c, 290.5, 318.0, d["punktsumme_einfach"], size=9, center=True)
    draw(c, 511.0, 318.0, d["punktsumme_zweifach"], size=9, center=True)
    # Result boxes: Gesamtergebnis (E) gray cell 269.7-311.7 top 354.9-408.4,
    # Durchschnittsnote gray cell 490.7-531.2 same rows
    draw(c, 290.5, 372.0, d["gesamtergebnis"], size=10, center=True)
    if d.get("durchschnittsnote_ziffer"):
        draw(c, 511.0, 372.0, d["durchschnittsnote_ziffer"], size=10, center=True)
    draw(c, 160.0, 536.0, d["ort_datum"])
    # signature lines at top=600.2: x 72.6-264.1 (Tutor), 323.5-514.9 (Schulleiter)
    draw(c, 168.0, 588.0, d["tutor"], font="Helvetica-Oblique", center=True)
    draw(c, 419.0, 588.0, d["schulleiter"], font="Helvetica-Oblique", center=True)
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
    for idx, overlay_fn in ((CERT_PAGE, cert_overlay), (GRADES_PAGE, grades_overlay)):
        page = template.pages[idx]
        page.merge_page(PdfReader(overlay_fn(data)).pages[0])
        writer.add_page(page)

    out = out_dir / "kmk-fhr-schulischer-teil.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    rasterize(out, out_dir / "kmk-fhr-schulischer-teil-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
