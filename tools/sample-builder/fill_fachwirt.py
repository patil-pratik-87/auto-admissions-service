# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf", "reportlab", "pyyaml", "pillow"]
# ///
"""Generate a 'Gepruefter Wirtschaftsfachwirt' Fortbildung Zeugnis (IHK house
format, modeled on samples/blank-documents/ihk-musterzeugnis.pdf) with synthetic applicant
data, and append the impersonal BIBB/Europass Zeugniserlaeuterung
(samples/blank-documents/bibb-wirtschaftsfachwirt.pdf) behind it — the typical real-world
upload is certificate + supplement.

The personal page carries the decision-relevant DQR/EQR Niveau 6 line.
Output:

  samples/filled-documents/<slug>/fachwirt-zeugnis.pdf        vector
  samples/filled-documents/<slug>/fachwirt-zeugnis-scan.pdf   150dpi raster ("scan")

Usage: uv run tools/sample-builder/fill_fachwirt.py samples/filled-documents/<slug>/<slug>.yaml
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

SUPPLEMENT = Path(__file__).resolve().parents[2] / "samples" / "blank-documents" / "bibb-wirtschaftsfachwirt.pdf"
PAGE_W, PAGE_H = 595.32, 842.04


def zeugnis_page(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    cx = PAGE_W / 2

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(cx, 780, d["chamber"])
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(cx, 720, "Zeugnis")
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, 700, "über die Prüfung zum anerkannten Fortbildungsberuf")
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, 676, d["qualification"])
    c.setFont("Helvetica", 10)
    c.drawCentredString(cx, 660, "nach §§ 53 ff. Berufsbildungsgesetz")

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, 616, d["name"])
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, 596, f"geboren am {d['birth_date']} in {d['birth_place']}")
    c.drawCentredString(cx, 572, "hat die Prüfung mit dem Gesamtergebnis")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(cx, 554, f"{d['gesamt_note']} ({d['gesamt_punkte']} Punkte)")
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, 536, "bestanden.")

    # Exam-part table: [Pruefungsteil, Note, Punkte]
    y = 496
    c.setFont("Helvetica-Bold", 10)
    c.drawString(90, y, "Prüfungsteil")
    c.drawString(400, y, "Note")
    c.drawRightString(505, y, "Punkte")
    c.setLineWidth(0.5)
    c.line(90, y - 5, 505, y - 5)
    y -= 22
    c.setFont("Helvetica", 10)
    for teil, note, punkte in d["pruefungsteile"]:
        c.drawString(90, y, teil)
        c.drawString(400, y, note)
        c.drawRightString(505, y, punkte)
        y -= 18

    # The fact the advanced-vocational rule hangs on. dqr_niveau overrides the
    # printed level; dqr_line: false omits the statement entirely (older
    # certificate style — the level must then be proven another way, if at all).
    y -= 14
    c.setFont("Helvetica", 10)
    if d.get("dqr_line", True):
        niveau = d.get("dqr_niveau", "6")
        c.drawString(90, y, "Dieser Abschluss ist im Deutschen und Europäischen Qualifikationsrahmen")
        c.drawString(90, y - 13, f"(DQR, EQR) dem Niveau {niveau} zugeordnet.")
        y -= 26
    # Optional extra statements (teaching-hour volume, admission prerequisite).
    for line in d.get("zusatz_lines", []):
        c.drawString(90, y, line)
        y -= 13

    y -= 29
    c.setFont("Helvetica", 11)
    c.drawString(90, y, d["ort_datum"])
    y -= 55
    c.setFont("Helvetica", 10)
    c.drawString(90, y, "Der Präsident")
    c.drawString(370, y, "Die Hauptgeschäftsführerin")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(90, y - 30, d["praesident"])
    c.drawString(370, y - 30, d["hauptgeschaeftsfuehrerin"])

    c.setFont("Helvetica", 6.5)
    c.drawCentredString(
        cx, 68,
        "100 - 92 Punkte Note 1 = sehr gut   unter 92 - 81 Punkte Note 2 = gut   "
        "unter 81 - 67 Punkte Note 3 = befriedigend",
    )
    c.drawCentredString(
        cx, 59,
        "unter 67 - 50 Punkte Note 4 = ausreichend   unter 50 - 30 Punkte "
        "Note 5 = mangelhaft   unter 30 Punkte Note 6 = ungenügend",
    )
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

    writer = PdfWriter()
    writer.add_page(PdfReader(zeugnis_page(data)).pages[0])
    # The BIBB Zeugniserlaeuterung is specific to the Wirtschaftsfachwirt;
    # supplement: false skips it for other Fortbildung qualifications.
    if data.get("supplement", True):
        for page in PdfReader(SUPPLEMENT).pages:
            writer.add_page(page)

    base = data.get("out_basename", "fachwirt-zeugnis")
    out = out_dir / f"{base}.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    rasterize(out, out_dir / f"{base}-scan.pdf")
    print(f"wrote {out} and scan variant")


if __name__ == "__main__":
    main()
