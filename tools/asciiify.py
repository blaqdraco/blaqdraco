import sys
from typing import List
from PIL import Image, ImageEnhance, ImageOps

# Simple image-to-ASCII converter with a few helpful flags
# Usage:
#   python asciiify.py input.jpg output.txt [width]
#   python asciiify.py input.jpg output.txt --width 90 --contrast 1.3 --autocontrast --invert

DEFAULT_ASCII = "@%#*+=-:. "  # darkest -> lightest


def parse_args(argv: List[str]):
    if len(argv) < 3:
        print(
            "Usage: python asciiify.py <input> <output> [width] [--width N] [--invert] [--contrast F] [--autocontrast] [--charset STR]"
        )
        sys.exit(1)
    input_path = argv[1]
    output_path = argv[2]
    width = None
    invert = False
    autocontrast = False
    contrast = None
    charset = DEFAULT_ASCII

    # support positional width as argv[3]
    i = 3
    if i < len(argv) and not argv[i].startswith("-"):
        try:
            width = int(argv[i])
            i += 1
        except ValueError:
            pass

    # parse flags
    while i < len(argv):
        arg = argv[i]
        if arg in ("--width", "-w") and i + 1 < len(argv):
            width = int(argv[i + 1])
            i += 2
        elif arg == "--invert":
            invert = True
            i += 1
        elif arg == "--autocontrast":
            autocontrast = True
            i += 1
        elif arg in ("--contrast", "-c") and i + 1 < len(argv):
            contrast = float(argv[i + 1])
            i += 2
        elif arg in ("--charset", "--chars") and i + 1 < len(argv):
            charset = argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {arg}")
            sys.exit(2)

    return input_path, output_path, width or 80, invert, autocontrast, contrast, charset


def resize(image: Image.Image, new_width=80) -> Image.Image:
    w, h = image.size
    aspect_ratio = h / max(1, w)
    new_height = int(aspect_ratio * new_width * 0.55)  # tweak for character aspect
    return image.resize((new_width, max(1, new_height)))


def preprocess(image: Image.Image, invert: bool, autocontrast: bool, contrast: float) -> Image.Image:
    img = image.convert("L")
    if autocontrast:
        img = ImageOps.autocontrast(img)
    if contrast is not None:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if invert:
        img = ImageOps.invert(img)
    return img


def pixels_to_ascii(image: Image.Image, charset: str) -> str:
    pixels = image.getdata()
    scale = (len(charset) - 1) / 255
    return "".join(charset[int(p * scale)] for p in pixels)


def convert(input_path: str, output_path: str, width=80, invert=False, autocontrast=False, contrast=None, charset=DEFAULT_ASCII):
    img = Image.open(input_path)
    img = resize(img, width)
    img = preprocess(img, invert=invert, autocontrast=autocontrast, contrast=contrast)
    ascii_str = pixels_to_ascii(img, charset)
    w, _ = img.size
    lines = [ascii_str[i:i + w] for i in range(0, len(ascii_str), w)]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    args = parse_args(sys.argv)
    convert(*args)
