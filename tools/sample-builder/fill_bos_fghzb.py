# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "reportlab", "pyyaml", "pillow"]
# ///
"""Fill the Bayern Anlage 17 'Zeugnis der fachgebundenen Hochschulreife'
(Berufsoberschule) Muster (samples/blank-documents/bos-bayern-fachgebundene-hzb.pdf) with
synthetic applicant data.

Template page 0 = title (school, Ausbildungsrichtung), page 1 = static study
entitlement text, page 2 = personal data + grades + attestation. No AcroForm;
text is overlaid at coordinates measured with pdfplumber. Variants:

  nicht_bestanden: true      patches "bestanden."/"verliehen." to the negated
                             wording (explicitly incomplete qualification)
  restriction_lines: [...]   extra printed validity-restriction statement
  smudge_issuing: true       drops the static page 1 (it names Bayern) and, in
                             the SCAN only, blots the school/Schulort line and
                             the Ort/Datum line so the issuing place cannot be
                             read

Output:
  samples/filled-documents/<slug>/fachgebundene-hzb-zeugnis.pdf        vector-filled
  samples/filled-documents/<slug>/fachgebundene-hzb-zeugnis-scan.pdf   150dpi raster

Usage: uv run tools/sample-builder/fill_bos_fghzb.py samples/filled-documents/<slug>/<slug>.yaml
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

TEMPLATE = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "bos-bayern-fachgebundene-hzb.pdf"
PAGE_W, PAGE_H = 595.32, 841.92


def row(c, x, top, text, size=10, center=False, font="Helvetica"):
    """Baseline aligned with printed words whose pdfplumber top is `top`."""
    c.setFont(font, size)
    y = PAGE_H - top - 8.5
    if center:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


def on_line(c, x, line_top, text, size=10, center=False, font="Helvetica"):
    """Baseline 2pt above a signature/date rule whose top is `line_top`."""
    c.setFont(font, size)
    y = PAGE_H - line_top + 2
    if center:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


def patch(c, x0, top, x1, text, size=11):
    """White-out printed template text and rewrite it (for nicht_bestanden).
    Times-Roman matches the template's serif body face."""
    c.setFillColorRGB(1, 1, 1)
    c.rect(x0 - 1.5, PAGE_H - top - 11.5, x1 - x0 + 3, 13, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Times-Roman", size)
    c.drawString(x0, PAGE_H - top - 8.5, text)


def title_overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    on_line(c, 297.0, 137.0, d["school"], size=11, center=True)
    on_line(c, 297.0, 263.0, d["ausbildungsrichtung"], size=11, center=True)
    c.save()
    buf.seek(0)
    return buf


# Grades table between the printed headers (top 242.5) and the Seminararbeit
# line (top 384.4): left columns Fach/Note/Punkte and right columns.
GRADE_ROW_TOP, GRADE_ROW_STEP = 264.0, 17.0
LEFT_COLS = (90.0, 210.0, 279.0)   # fach x, note center, punkte center
RIGHT_COLS = (340.0, 450.0, 519.0)


def main_overlay(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    row(c, 125.0, 106.7, d["name"], size=11)
    row(c, 161.0, 150.4, d["birth_date"], size=11, center=True)
    row(c, 318.0, 150.4, d["birth_place"], size=11, center=True)
    row(c, 262.0, 173.3, d["klasse"], size=11, center=True)
    row(c, 165.0, 196.4, d["ausbildungsrichtung"], size=11)
    for cols, faecher in ((LEFT_COLS, d["faecher_links"]),
                          (RIGHT_COLS, d["faecher_rechts"])):
        for i, (fach, note, punkte) in enumerate(faecher):
            top = GRADE_ROW_TOP + i * GRADE_ROW_STEP
            row(c, cols[0], top, fach, size=9.5)
            row(c, cols[1], top, note, size=9.5, center=True)
            row(c, cols[2], top, punkte, size=9.5, center=True)
    sem = d["seminararbeit"]
    row(c, 186.0, 384.4, sem["thema"], size=10)
    row(c, 105.0, 401.7, sem["note"], size=10)
    row(c, 215.0, 401.7, sem["punkte"], size=10)
    row(c, 125.0, 424.6, d["name"], size=11)
    if d.get("nicht_bestanden"):
        # "nicht bestanden." is wider than the printed "bestanden.", so the
        # whole sentence line is rewritten to keep the spacing intact.
        patch(c, 70.9, 436.1, 360.1,
              "hat die Abiturprüfung nicht bestanden. Der Prüfungsausschuss hat ihm/ihr die")
        patch(c, 70.9, 469.4, 110.6, "nicht verliehen.")
    # Durchschnittsnote blanks ".....,...." / "(i.W.: ...)" at top 492.4
    if d.get("durchschnittsnote_ziffer"):
        row(c, 290.0, 492.4, d["durchschnittsnote_ziffer"], size=10, center=True)
        row(c, 340.0, 492.4, d["durchschnittsnote_text"], size=10)
    # Free band between the Durchschnittsnote row (492.4) and the Ort/Datum
    # entry (~515.9): fits one 9pt line.
    for i, line in enumerate(d.get("restriction_lines", [])):
        row(c, 70.9, 504.0 + i * 10.5, line, size=9)
    on_line(c, 70.9, 526.9, d["ort_datum"], size=10)
    on_line(c, 177.0, 595.9, d["vorsitz"], size=10, center=True,
            font="Helvetica-Oblique")
    on_line(c, 456.0, 595.9, d["schulleiter"], size=10, center=True,
            font="Helvetica-Oblique")
    c.save()
    buf.seek(0)
    return buf


def smudge(img, rect, dpi=150):
    """Irregular dark ink blot over `rect` (PDF pts, y from bottom)."""
    s = dpi / 72.0
    x0, y0, x1, y1 = rect
    left, right = x0 * s, x1 * s
    top, bottom = (PAGE_H - y1) * s, (PAGE_H - y0) * s
    dr = ImageDraw.Draw(img)
    h = bottom - top
    dr.ellipse([left, top + h * 0.05, right, bottom - h * 0.1], fill=(45, 42, 48))
    dr.ellipse([left + (right - left) * 0.2, top, right, bottom - h * 0.3],
               fill=(58, 54, 60))
    dr.ellipse([left, top + h * 0.3, right - (right - left) * 0.15, bottom],
               fill=(38, 36, 42))
    return img


# (output page index, rect) blots for smudge_issuing: the school/Schulort line
# on the title page and the Ort/Datum line on the attestation page.
ISSUING_SMUDGES = [
    (0, (128.0, PAGE_H - 143.0, 467.0, PAGE_H - 125.0)),
    (1, (68.0, PAGE_H - 529.9 - 3.0, 222.0, PAGE_H - 526.9 + 13.0)),
]


def rasterize(pdf_path, out_path, smudges=(), dpi=150):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), f"{td}/p"],
            check=True,
        )
        pages = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("p*.png"))]
        for idx, rect in smudges:
            pages[idx] = smudge(pages[idx], rect, dpi)
        pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=dpi)


def main():
    data = yaml.safe_load(Path(sys.argv[1]).read_text())
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / data["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    template = PdfReader(TEMPLATE)
    writer = PdfWriter()
    page0 = template.pages[0]
    page0.merge_page(PdfReader(title_overlay(data)).pages[0])
    writer.add_page(page0)
    if not data.get("smudge_issuing"):
        writer.add_page(template.pages[1])  # static entitlement text
    page2 = template.pages[2]
    page2.merge_page(PdfReader(main_overlay(data)).pages[0])
    writer.add_page(page2)

    out = out_dir / "fachgebundene-hzb-zeugnis.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    smudges = ISSUING_SMUDGES if data.get("smudge_issuing") else ()
    rasterize(out, out_dir / "fachgebundene-hzb-zeugnis-scan.pdf", smudges)
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
