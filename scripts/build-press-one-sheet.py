from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "press" / "assets" / "ghost-orgy-one-sheet.pdf"
COVER = ROOT / "press" / "assets" / "ghost-orgy-salt-cover-3000.jpg"
FONTS = ROOT / "fonts"

BG = (0.015, 0.016, 0.018)
FG = (0.94, 0.91, 0.86)
MUTED = (0.68, 0.63, 0.59)
LINE = (0.18, 0.18, 0.18)
ACCENT = (0.54, 1.0, 0.76)
RUST = (0.74, 0.39, 0.22)


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("PlexSans", str(FONTS / "ibm-plex-sans-400.ttf")))
    pdfmetrics.registerFont(TTFont("PlexSansMedium", str(FONTS / "ibm-plex-sans-500.ttf")))
    pdfmetrics.registerFont(TTFont("PlexSansBold", str(FONTS / "ibm-plex-sans-600.ttf")))
    pdfmetrics.registerFont(TTFont("PlexMono", str(FONTS / "ibm-plex-mono-400.ttf")))


def set_rgb(c: canvas.Canvas, rgb: tuple[float, float, float]) -> None:
    c.setFillColorRGB(*rgb)
    c.setStrokeColorRGB(*rgb)


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width_chars: int,
    line_height: float,
    font: str,
    size: float,
    color: tuple[float, float, float],
) -> float:
    c.setFont(font, size)
    set_rgb(c, color)
    for line in wrap(text, width_chars):
        c.drawString(x, y, line)
        y -= line_height
    return y


def draw_label(c: canvas.Canvas, text: str, x: float, y: float, color=ACCENT) -> None:
    c.setFont("PlexSansBold", 9)
    set_rgb(c, color)
    c.drawString(x, y, text.upper())


def draw_box(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setLineWidth(0.7)
    c.setStrokeColorRGB(*LINE)
    c.rect(x, y, w, h, stroke=1, fill=0)


def main() -> None:
    register_fonts()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(OUT), pagesize=letter)
    w, h = letter

    c.setFillColorRGB(*BG)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    c.setStrokeColorRGB(*RUST)
    c.setLineWidth(1.8)
    c.line(42, 48, 42, h - 42)

    c.setStrokeColorRGB(*LINE)
    c.setLineWidth(0.6)
    c.line(60, h - 56, w - 54, h - 56)
    c.line(60, 104, w - 60, 104)

    x = 62
    top = h - 80
    draw_label(c, "Electronic Press Kit", x, top)

    c.setFont("PlexSansBold", 35)
    set_rgb(c, FG)
    c.drawString(x, top - 34, "GHOST ORGY")

    c.setFont("PlexSans", 11.5)
    set_rgb(c, MUTED)
    c.drawString(x, top - 55, "Phoenix experimental post-hardcore by Jack Dyer")
    c.drawString(x, top - 72, "Art-damaged hardcore / literary heavy music / die-fi")

    box_w = 278
    draw_box(c, x, 488, box_w, 78)
    draw_label(c, "Current Release", x + 13, 545)
    c.setFont("PlexSansBold", 18)
    set_rgb(c, FG)
    c.drawString(x + 13, 523, "Salt")
    c.setFont("PlexSans", 10.5)
    set_rgb(c, MUTED)
    c.drawString(x + 13, 506, "Debut album - released May 29, 2026")

    draw_box(c, x, 416, box_w, 52)
    draw_label(c, "Best Start", x + 13, 450)
    c.setFont("PlexSansBold", 13)
    set_rgb(c, FG)
    c.drawString(x + 13, 432, "The Sky That Fears Us")

    cover_x = 372
    cover_y = 522
    cover_size = 184
    c.drawImage(ImageReader(str(COVER)), cover_x, cover_y, cover_size, cover_size, preserveAspectRatio=True, anchor="c")
    draw_box(c, cover_x, cover_y, cover_size, cover_size)

    draw_label(c, "RIYL", cover_x, 502)
    riyl = [
        "Refused",
        "Give Up the Ghost",
        "The Blood Brothers",
        "early mewithoutYou",
        "Modern Life Is War",
        "The Sound of Animals Fighting",
    ]
    c.setFont("PlexSans", 10.5)
    set_rgb(c, FG)
    ry = 488
    for item in riyl:
        c.drawString(cover_x, ry, item)
        ry -= 12.5

    y = 378
    draw_label(c, "Press Angles", x, y, RUST)
    y -= 17
    c.setFont("PlexSansBold", 10.8)
    set_rgb(c, FG)
    for line in [
        "Phoenix heavy music with an unusually built world.",
        "Art-damaged hardcore shaped into horror-mythic album architecture.",
        "Select licensing and collaborations when the context can carry the work.",
    ]:
        c.drawString(x, y, line)
        y -= 14

    y -= 18
    draw_label(c, "Short Bio", x, y)
    y -= 15
    bio = (
        "Ghost Orgy is a Phoenix-based experimental post-hardcore project by Jack Dyer. "
        "The sound sits near Refused, Give Up the Ghost, The Blood Brothers, early "
        "mewithoutYou, Modern Life Is War, and The Sound of Animals Fighting, then folds "
        "that pressure into horror-mythic world-building and damaged, die-fi texture."
    )
    draw_wrapped(c, bio, x, y, 86, 11.5, "PlexSans", 9.5, MUTED)

    c.setFont("PlexSansBold", 10)
    set_rgb(c, FG)
    c.drawString(x, 85, "Press / licensing / booking / commissions: info@unholyghost.org")

    c.setFont("PlexSans", 8.2)
    set_rgb(c, MUTED)
    c.drawString(x, 69, "Press: unholyghost.org/press")
    c.drawString(x + 142, 69, "Listen: unholyghost.org/listen")
    c.drawString(x, 55, "Bandcamp: ghostorgy.bandcamp.com/album/salt")

    c.setFont("PlexSansBold", 8.2)
    set_rgb(c, RUST)
    c.drawRightString(w - 60, 55, "GHOST ORGY LLC")

    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
