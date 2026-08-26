# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "pyyaml", "pillow"]
# ///
"""Generate a VHS-style Teilnahmebescheinigung: a plain participation
certificate for a short course, explicitly without an exam. Deliberately
matches NO rule selector — not a school qualification, not a vocational
training, not a Fortbildungspruefung — so a bundle containing only this
document exercises the NO_RECOGNIZED_RULE resolution branch. Output:

  samples/filled-documents/<slug>/teilnahmebescheinigung.pdf        (+ -scan.pdf)

Usage: uv run tools/sample-builder/make_teilnahmebescheinigung.py samples/filled-documents/<slug>/<slug>.yaml
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
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, H - 80, d["veranstalter"])
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, H - 95, d["veranstalter_adresse"])
    c.setLineWidth(0.8)
    c.line(MARGIN, H - 106, W - MARGIN, H - 106)

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, H - 180, "Teilnahmebescheinigung")

    c.setFont("Helvetica", 11)
    y = H - 240
    for line in (
        f"{d['anrede']} {d['name']}, geboren am {d['birth_date']},",
        "hat an dem Kurs",
    ):
        c.drawCentredString(W / 2, y, line)
        y -= 18
    y -= 8
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W / 2, y, d["kurs"])
    y -= 26
    c.setFont("Helvetica", 11)
    for line in (
        f"im Zeitraum vom {d['zeitraum']}",
        f"im Umfang von {d['umfang']} regelmäßig teilgenommen.",
    ):
        c.drawCentredString(W / 2, y, line)
        y -= 18
    y -= 14
    c.drawCentredString(W / 2, y, "Eine Prüfung wurde nicht abgelegt.")

    y -= 70
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, y, d["ort_datum"])
    y -= 50
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(MARGIN, y, d["unterzeichner"])
    c.setLineWidth(0.6)
    c.line(MARGIN, y - 4, MARGIN + 160, y - 4)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y - 16, d["unterzeichner_titel"])
    c.drawString(MARGIN, y - 28, d["veranstalter"])
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
    out = out_dir / "teilnahmebescheinigung.pdf"
    build(d, out)
    rasterize(out, out_dir / "teilnahmebescheinigung-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
