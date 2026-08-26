# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "pyyaml", "pillow"]
# ///
"""Fill the BA Arbeitsbescheinigung (samples/blank-documents/ba-arbeitsbescheinigung.pdf,
official § 312 SGB III form, BA II 2 08/2023) with synthetic applicant data.

Unlike the other templates this form HAS AcroForm fields, so values are
filled directly by field name (the persona YAML lists them under ba.fields);
unlisted fields stay empty, as real employer submissions often are. Output:

  samples/filled-documents/<slug>/ba-arbeitsbescheinigung.pdf        vector, form-filled
  samples/filled-documents/<slug>/ba-arbeitsbescheinigung-scan.pdf   150dpi raster ("scan")

ba.smudge_end_date: true degrades ONLY the scan: an ink blot is drawn over
the day digits of field 30 "bis" (page 2), leaving month/year legible - the
FIELD_ILLEGIBLE / UNKNOWN-beats-close-fail specimen (tuple 26). The vector
PDF stays pristine (the degradation models a bad scan of a clean original).

Usage: uv run tools/sample-builder/fill_ba_arbeitsbescheinigung.py samples/filled-documents/daniel-roth/daniel-roth.yaml
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject

TEMPLATE = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "ba-arbeitsbescheinigung.pdf"
PAGE_H = 841.89
DPI = 150

# Field 30 "bis" rect on page index 1 is x 309-384, y 475.9-493.9 (PDF pts,
# y from bottom); its value renders left-aligned from ~x 311, day digits end
# ~x 331. The blot must cover ONLY the day - month/year stay legible.
SMUDGE_PDF_RECT = (305.0, 474.0, 326.0, 496.0)


def smudge(img, page_h_pt=PAGE_H, dpi=DPI):
    """Draw an irregular dark ink blot over the day part of the end date."""
    s = dpi / 72.0
    x0, y0, x1, y1 = SMUDGE_PDF_RECT
    left, right = x0 * s, x1 * s
    top, bottom = (page_h_pt - y1) * s, (page_h_pt - y0) * s
    d = ImageDraw.Draw(img)
    h = bottom - top
    # overlapping ellipses read as a smeared ink blot; keep every ellipse
    # inside [left, right] horizontally so the month digits survive
    d.ellipse([left, top + h * 0.05, right, bottom - h * 0.1], fill=(45, 42, 48))
    d.ellipse([left + (right - left) * 0.2, top, right, bottom - h * 0.3],
              fill=(58, 54, 60))
    d.ellipse([left, top + h * 0.3, right - (right - left) * 0.15, bottom],
              fill=(38, 36, 42))
    return img


def rasterize(pdf_path, out_path, do_smudge, dpi=DPI):
    """Simulate an uploaded scan: rasterize and re-wrap as PDF."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), f"{td}/p"],
            check=True,
        )
        pages = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("p*.png"))]
        if do_smudge:
            pages[1] = smudge(pages[1])
        pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=dpi)


def main():
    data = yaml.safe_load(Path(sys.argv[1]).read_text())
    ba = data["ba"]
    out_dir = Path(__file__).resolve().parents[2] / "samples" / "filled-documents" / data["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(TEMPLATE)
    writer = PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, ba["fields"])
    # belt and braces: let viewers regenerate appearances too
    writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)

    out = out_dir / "ba-arbeitsbescheinigung.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    rasterize(out, out_dir / "ba-arbeitsbescheinigung-scan.pdf",
              do_smudge=bool(ba.get("smudge_end_date")))
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
