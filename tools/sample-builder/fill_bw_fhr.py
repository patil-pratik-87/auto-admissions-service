# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "reportlab", "pyyaml", "pillow"]
# ///
"""Fill the Baden-Wuerttemberg 'Zeugnis der Fachhochschulreife' template
(samples/blank-documents/bw-fhsr.pdf) with synthetic applicant data.

Page 1 is the certificate (filled here); page 2 is the static Rueckseite
(formula + Durchschnittsnote table) and is passed through unchanged. The
template's own "Muster" watermark is deliberately kept. Text is overlaid at
coordinates measured from the original PDF. Output:

  samples/filled-documents/<slug>/bw-fhr-zeugnis.pdf        vector-filled
  samples/filled-documents/<slug>/bw-fhr-zeugnis-scan.pdf   150dpi raster ("scan")

Usage: uv run tools/sample-builder/fill_bw_fhr.py samples/filled-documents/erika-musterfrau/erika-musterfrau.yaml
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

TEMPLATE = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "bw-fhsr.pdf"
PAGE_H = 841.92

# Helvetica's built-in encoding lacks e.g. Turkish dotless i; embed a system
# TTF with wider coverage when available. Each face is checked separately —
# a present Arial.ttf does not guarantee Arial Italic.ttf.
_ARIAL = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
_ARIAL_ITALIC = _ARIAL.parent / "Arial Italic.ttf"
FONT, FONT_ITALIC = "Helvetica", "Helvetica-Oblique"
if _ARIAL.exists():
    pdfmetrics.registerFont(TTFont("Fill", str(_ARIAL)))
    FONT = "Fill"
if _ARIAL_ITALIC.exists():
    pdfmetrics.registerFont(TTFont("Fill-Italic", str(_ARIAL_ITALIC)))
    FONT_ITALIC = "Fill-Italic"


def check_encodable(obj):
    """With a built-in Type1 fallback, non-Latin-1 text (e.g. 'Yılmaz') would
    silently render as a ZapfDingbats box — fail loudly instead."""
    if isinstance(obj, str):
        try:
            obj.encode("latin-1")
        except UnicodeEncodeError:
            sys.exit(f"'{obj}' is outside Latin-1; built-in Helvetica would "
                     "corrupt it — install Arial or provide another TTF")
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            check_encodable(v)
    elif isinstance(obj, dict):
        for v in obj.values():
            check_encodable(v)


def draw(c, x, top, text, size=11, font=None, center=False):
    font = font or FONT
    c.setFont(font, size)
    y = PAGE_H - top - 9.5
    if center:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


# Kursleistungen table: Fach x 68.1-273.1 | Schulhalbjahr cols 273.1-383.2 and
# 383.2-493.5. Section I rows (tops): 2 rows; section II rows: 7 rows.
SEC1_ROWS = [398.7, 411.9]
SEC2_ROWS = [451.5, 464.7, 478.0, 491.2, 504.5, 517.8, 531.0]
COL1_X, COL2_X = 328.0, 438.0  # cell centers


def overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595.32, PAGE_H))
    draw(c, 254.0, 45.0, d["school"], size=9)
    draw(c, 258.0, 139.5, d["name"])
    draw(c, 258.0, 163.5, d["birth_date"])
    draw(c, 258.0, 187.5, d["birth_place"])
    # "Schulhalbjahr ___" header blanks at x 354.4-371.0 / 464.7-481.3
    draw(c, 362.7, 337.0, d["halbjahr_1"], size=10, center=True)
    draw(c, 473.0, 337.0, d["halbjahr_2"], size=10, center=True)
    for rows, subjects in ((SEC1_ROWS, d["subjects_i"]), (SEC2_ROWS, d["subjects_ii"])):
        for row, (fach, g1, g2) in zip(rows, subjects):
            draw(c, 74.0, row + 1.0, fach, size=10)
            if g1:
                draw(c, COL1_X, row + 1.0, g1, size=10, center=True)
            if g2:
                draw(c, COL2_X, row + 1.0, g2, size=10, center=True)
    # Punktsumme value cell 273.1-383.2, Gesamtergebnis value cell 494-556.4,
    # row spans top 563.7-578.7
    draw(c, 328.0, 561.5, d["punktsumme"], size=10, center=True)
    draw(c, 525.0, 561.5, d["gesamtergebnis"], size=10, center=True)
    # Durchschnittsnote blanks at top=589.8: Ziffern ~x 344.8-400, Buchstaben
    # inside parentheses ~x 400-546
    if d.get("durchschnittsnote_ziffer"):
        draw(c, 372.0, 580.5, d["durchschnittsnote_ziffer"], size=10, center=True)
        draw(c, 473.0, 580.5, d["durchschnittsnote_text"], size=10, center=True)
    # Fremdsprachen free area below label at top=619.8
    for i, line in enumerate(d.get("fremdsprachen", [])):
        draw(c, 78.0, 634.0 + i * 13, line, size=10)
    draw(c, 75.0, 667.5, d["datum"])
    # Schulleiter signature line x 408.6-552.9 at top=676.8
    draw(c, 480.0, 667.5, d["schulleiter"], font=FONT_ITALIC, center=True)
    # Optional replacement of the printed recognition clause ("... in allen
    # Ländern mit Ausnahme von Bayern und Sachsen.", x 68.3-443.5 at top 796)
    # for validity-restriction variants.
    if d.get("anerkennung_clause"):
        c.setFillColorRGB(1, 1, 1)
        c.rect(66.0, PAGE_H - 804.5, 465.0, 10.5, stroke=0, fill=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont(FONT, 7)
        c.drawString(68.3, PAGE_H - 802.9, d["anerkennung_clause"])
    c.save()
    buf.seek(0)
    return buf


def rasterize(pdf_path, out_path, dpi=150):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), f"{td}/p"],
            check=True,
        )
        pages = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("p*.png"))]
        pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=dpi)


def main():
    data = yaml.safe_load(Path(sys.argv[1]).read_text())
    if "Helvetica" in (FONT, FONT_ITALIC):
        check_encodable(data)
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / data["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    template = PdfReader(TEMPLATE)
    writer = PdfWriter()
    page = template.pages[0]
    page.merge_page(PdfReader(overlay(data)).pages[0])
    writer.add_page(page)
    writer.add_page(template.pages[1])  # static Rueckseite

    out = out_dir / "bw-fhr-zeugnis.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    rasterize(out, out_dir / "bw-fhr-zeugnis-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
