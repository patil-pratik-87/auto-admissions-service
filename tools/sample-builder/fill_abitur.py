# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "reportlab", "pyyaml", "pillow"]
# ///
"""Fill the KMK 'Zeugnis der Allgemeinen Hochschulreife' Musterentwurf
(samples/blank-documents/kmk-abitur.pdf, i.d.F. 06.06.2024) with synthetic applicant data.

The template has no AcroForm fields, so text is overlaid at hard-coded
coordinates measured from the original PDF (pdfplumber). The Musterentwurf
header is deliberately kept, matching the other fill scripts. Output:

  samples/filled-documents/<slug>/abitur-zeugnis.pdf        vector-filled
  samples/filled-documents/<slug>/abitur-zeugnis-scan.pdf   150dpi raster ("scan")

Usage: uv run tools/sample-builder/fill_abitur.py samples/filled-documents/felix-brandt/felix-brandt.yaml
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

TEMPLATE = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "kmk-abitur.pdf"
PAGE_H = 841.92

# Template page indices: 2 = title page ("-3-"), 3/4 = Block I grade tables,
# 5 = Block II + Gesamtqualifikation ("-6a-", four Pruefungsfaecher variant),
# 7 = Fremdsprachen + attestation/signatures ("-7-").
FILL_PAGES = (2, 3, 4, 5, 7)


def row(c, x, top, text, size=10, center=False):
    """Baseline aligned with a printed word whose pdfplumber top is `top`."""
    c.setFont("Helvetica", size)
    y = PAGE_H - top - 9
    if center:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


def on_line(c, x, line_top, text, size=10, center=False):
    """Baseline 2pt above an underscore rule whose top is `line_top`."""
    c.setFont("Helvetica", size)
    y = PAGE_H - line_top + 2
    if center:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


def new_canvas():
    buf = io.BytesIO()
    return buf, canvas.Canvas(buf, pagesize=(595.32, PAGE_H))


def title_overlay(d):
    buf, c = new_canvas()
    # School name goes just below the rule: the Musterentwurf meta-header sits
    # too close above it for on-line placement.
    row(c, 294.9, 141.0, d["school"], center=True)
    on_line(c, 294.9, 244.7, d["name"], size=11, center=True)
    row(c, 130.0, 275.1, d["birth_date"])
    row(c, 285.0, 275.1, d["birth_place"])
    row(c, 140.0, 305.5, d["address"])
    c.save()
    buf.seek(0)
    return buf


# Block I rows: printed subject label top and label x1 (for the eA tag).
# Page idx 3 = sprachlich/gesellschaftswissenschaftlich, idx 4 = math/nat/Sport.
BLOCK_I_ROWS = {
    3: {
        "deutsch": (279.6, 158.7),
        "englisch": (299.8, 159.8),
        "franzoesisch": (320.2, 176.9),
        "latein": (340.6, 148.3),
        "musik": (360.9, 147.3),
        "bildende_kunst": (381.3, 191.1),
        "geschichte": (456.0, 172.8),
        "sozialkunde_politik": (476.4, 208.8),
        "geographie": (496.7, 175.3),
    },
    4: {
        "mathematik": (219.3, 174.6),
        "physik": (239.6, 150.9),
        "chemie": (260.0, 156.3),
        "biologie": (280.3, 157.2),
        "informatik": (300.7, 166.1),
        "religion_ethik": (341.7, 188.1),
        "sport": (362.7, 144.8),
    },
}
# Halbjahr column centers per page (columns differ slightly between pages).
HJ_COLS = {3: (308.8, 376.5, 444.2, 511.6), 4: (303.7, 372.8, 441.9, 510.8)}


def block_i_overlay(page_idx, d):
    buf, c = new_canvas()
    row(c, 165.0, 85.4, d["name"])
    for key, (top, label_x1) in BLOCK_I_ROWS[page_idx].items():
        if key not in d["block_i"]:
            continue
        if key in d.get("ea_subjects", []):
            row(c, label_x1 + 6, top, "(eA)", size=9)
        for x, punkte in zip(HJ_COLS[page_idx], d["block_i"][key]):
            if punkte:
                row(c, x, top, punkte, size=9, center=True)
    c.save()
    buf.seek(0)
    return buf


# Block II exam table: PF1-PF4 row tops; columns schriftlich | muendlich |
# Gesamtergebnis. Calculation lines (x 350.9-414.7) at the listed tops.
PF_ROW_TOPS = (189.3, 209.7, 230.0, 250.4)
CALC_LINES = {"block_i": 499.2, "block_ii": 560.1, "gesamt": 605.8, "note": 636.5}


def block_ii_overlay(d):
    buf, c = new_canvas()
    row(c, 165.0, 92.0, d["name"])
    for top, (fach, schr, muendl, gesamt) in zip(PF_ROW_TOPS, d["pruefungsfaecher"]):
        row(c, 110.0, top, fach, size=9)
        if schr:
            row(c, 277.0, top, schr, size=9, center=True)
        if muendl:
            row(c, 375.5, top, muendl, size=9, center=True)
        row(c, 476.8, top, gesamt, size=9, center=True)
    on_line(c, 382.8, CALC_LINES["block_i"], d["block_i_punktsumme"], center=True)
    on_line(c, 382.8, CALC_LINES["block_ii"], d["block_ii_punktsumme"], center=True)
    on_line(c, 382.8, CALC_LINES["gesamt"], d["gesamtpunktzahl"], center=True)
    # Durchschnittsnote line: optional — omit in the YAML to produce an
    # ABSENT-field specimen (extraction should yield status ABSENT, not a guess).
    if d.get("durchschnittsnote"):
        on_line(c, 382.8, CALC_LINES["note"], d["durchschnittsnote"], center=True)
    c.save()
    buf.seek(0)
    return buf


# Fremdsprachen table data-row tops; columns Fach | Jahrgangsstufe | Niveau GER.
FS_ROW_TOPS = (183.0, 200.0, 217.0)


def final_overlay(d):
    buf, c = new_canvas()
    row(c, 165.0, 92.0, d["name"])
    for top, (fach, jgst, niveau) in zip(FS_ROW_TOPS, d["fremdsprachen"]):
        row(c, 85.0, top, fach, size=9)
        row(c, 327.0, top, jgst, size=9, center=True)
        row(c, 467.5, top, niveau, size=9, center=True)
    if d.get("bemerkungen"):
        on_line(c, 148.0, 325.2, d["bemerkungen"])
    on_line(c, 290.0, 370.6, d["anrede_name"], size=11, center=True)
    row(c, 110.0, 431.0, d["ort_datum"])
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(167.0, PAGE_H - 484.0, d["vorsitz"])
    c.drawCentredString(452.0, PAGE_H - 484.0, d["schulleiter"])
    c.save()
    buf.seek(0)
    return buf


def smudge(img, rect, dpi=150):
    """Draw an irregular dark ink blot over `rect` (PDF pts, y from bottom)."""
    s = dpi / 72.0
    x0, y0, x1, y1 = rect
    left, right = x0 * s, x1 * s
    top, bottom = (PAGE_H - y1) * s, (PAGE_H - y0) * s
    d = ImageDraw.Draw(img)
    h = bottom - top
    d.ellipse([left, top + h * 0.05, right, bottom - h * 0.1], fill=(45, 42, 48))
    d.ellipse([left + (right - left) * 0.2, top, right, bottom - h * 0.3],
              fill=(58, 54, 60))
    d.ellipse([left, top + h * 0.3, right - (right - left) * 0.15, bottom],
              fill=(38, 36, 42))
    return img


def rasterize(pdf_path, out_path, dpi=150, smudge_spec=None):
    """Simulate an uploaded scan: rasterize and re-wrap as PDF.
    smudge_spec = (output_page_index, rect) degrades ONLY the scan."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), f"{td}/p"],
            check=True,
        )
        pages = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("p*.png"))]
        if smudge_spec:
            idx, rect = smudge_spec
            pages[idx] = smudge(pages[idx], rect, dpi)
        pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=dpi)


def bemerkungen_smudge_rect(d):
    """Blot covering the tail of the Bemerkungen line from just after the
    substring named by `bemerkungen_smudge_after` (e.g. the Land name in a
    stated validity restriction) to the end of the line."""
    text = d["bemerkungen"]
    cut = text.index(d["bemerkungen_smudge_after"]) + len(d["bemerkungen_smudge_after"])
    x0 = 148.0 + stringWidth(text[:cut], "Helvetica", 10) - 2.0
    x1 = 148.0 + stringWidth(text, "Helvetica", 10) + 4.0
    # on_line baseline for top 325.2 is PAGE_H - 325.2 + 2; cover the 10pt line
    y_base = PAGE_H - 325.2 + 2
    return (x0, y_base - 4.0, x1, y_base + 11.0)


def main():
    data = yaml.safe_load(Path(sys.argv[1]).read_text())
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / data["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    overlays = {
        2: title_overlay(data),
        3: block_i_overlay(3, data),
        4: block_i_overlay(4, data),
        5: block_ii_overlay(data),
        7: final_overlay(data),
    }
    template = PdfReader(TEMPLATE)
    writer = PdfWriter()
    for idx in FILL_PAGES:
        page = template.pages[idx]
        page.merge_page(PdfReader(overlays[idx]).pages[0])
        writer.add_page(page)

    out = out_dir / "abitur-zeugnis.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    # The Bemerkungen line sits on the last output page (template page 7).
    spec = None
    if data.get("bemerkungen_smudge_after"):
        spec = (len(FILL_PAGES) - 1, bemerkungen_smudge_rect(data))
    rasterize(out, out_dir / "abitur-zeugnis-scan.pdf", smudge_spec=spec)
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
