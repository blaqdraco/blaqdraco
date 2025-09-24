import argparse
from pathlib import Path
from html import escape

# Convert ASCII art (monochrome text) to a colored SVG with gradient fill, stroke, glow, and optional animation.
# Usage examples:
#   python tools/ascii_to_svg.py tools/ascii-portrait.txt assets/portrait-neon.svg --theme neon --animate
#   python tools/ascii_to_svg.py tools/ascii-portrait.txt assets/portrait-arsenal.svg --theme arsenal

THEMES = {
    # Cyber/neon on dark
    "neon": {
        "fg": "#00E5FF",
        "fg2": "#8A2BE2",
        "bg": "#0B0F14",
        "glow": True,
        "stroke": "#001219",
    },
    # Arsenal-inspired red->gold on deep navy
    "arsenal": {
        "fg": "#EF0107",
        "fg2": "#FFC72C",
        "bg": "#031A3E",
        "glow": True,
        "stroke": "#000814",
    },
    "matrix": {
        "fg": "#00FF41",
        "fg2": "#00B33C",
        "bg": "#000000",
        "glow": False,
        "stroke": "#001100",
    },
    "sunset": {
        "fg": "#FF7E5F",
        "fg2": "#FEB47B",
        "bg": "#0B0F14",
        "glow": True,
        "stroke": "#2a0a0a",
    },
    "gold": {
        "fg": "#FFD700",
        "fg2": "#FF8C00",
        "bg": "#0B0F14",
        "glow": True,
        "stroke": "#332400",
    },
}


def build_svg(
    text: str,
    fg: str,
    bg: str,
    font_family: str,
    font_size: int,
    line_height: float,
    glow: bool,
    gradient: bool,
    fg2: str | None = None,
    stroke: str | None = None,
    stroke_width: float = 0.0,
    glow_size: float = 2.5,
    animate: bool = False,
    padding: int = 20,
):
    lines = text.splitlines()
    width_chars = max((len(l) for l in lines), default=0)
    height_lines = len(lines)

    # Character cell size approximation (monospace)
    char_w = font_size * 0.6
    char_h = font_size * line_height

    svg_w = int(width_chars * char_w + padding * 2)
    svg_h = int(height_lines * char_h + padding * 2)

    defs = []
    if gradient:
        if not fg2:
            fg2 = "#8A2BE2"
        grad_animate = (
            "<animateTransform attributeName='gradientTransform' type='rotate' from='0 0.5 0.5' to='360 0.5 0.5' dur='20s' repeatCount='indefinite'/>"
            if animate
            else ""
        )
        defs.append(
            f"""
            <linearGradient id='grad' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='{fg}'/>
              <stop offset='100%' stop-color='{fg2}'/>
              {grad_animate}
            </linearGradient>
            """
        )
    if glow:
        defs.append(
            f"""
            <filter id='glow' x='-50%' y='-50%' width='200%' height='200%'>
              <feGaussianBlur stdDeviation='{glow_size}' result='coloredBlur'/>
              <feMerge>
                <feMergeNode in='coloredBlur'/>
                <feMergeNode in='SourceGraphic'/>
              </feMerge>
            </filter>
            """
        )

    fill = "url(#grad)" if gradient else fg
    filter_attr = " filter='url(#glow)'" if glow else ""
    stroke_attr = (
        f" stroke='{stroke}' stroke-width='{stroke_width}' paint-order='stroke fill' stroke-linejoin='round'"
        if stroke and stroke_width > 0
        else ""
    )

    content = [f"<rect width='100%' height='100%' fill='{bg}'/>"]

    y = padding + font_size
    for line in lines:
        content.append(
            f"<text x='{padding}' y='{y:.0f}' fill='{fill}' font-family='{escape(font_family)}' font-size='{font_size}' xml:space='preserve' style='font-variant-ligatures:none' {filter_attr}{stroke_attr}>"
            + escape(line) + "</text>"
        )
        y += char_h

    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{svg_w}' height='{svg_h}' viewBox='0 0 {svg_w} {svg_h}'>"
        + ("<defs>" + "".join(defs) + "</defs>" if defs else "")
        + "".join(content)
        + "</svg>"
    )
    return svg


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--theme', choices=sorted(THEMES.keys()))
    p.add_argument('--fg', default=None)
    p.add_argument('--fg2', default=None)
    p.add_argument('--bg', default=None)
    p.add_argument('--font', default='JetBrains Mono, Fira Code, Consolas, monospace')
    p.add_argument('--size', type=int, default=12)
    p.add_argument('--line-height', type=float, default=1.1)
    p.add_argument('--no-glow', action='store_true')
    p.add_argument('--no-gradient', action='store_true')
    p.add_argument('--stroke', default=None)
    p.add_argument('--stroke-width', type=float, default=0.0)
    p.add_argument('--glow-size', type=float, default=2.5)
    p.add_argument('--animate', action='store_true')
    p.add_argument('--padding', type=int, default=20)
    args = p.parse_args()

    cfg = {
        "fg": args.fg or "#00E5FF",
        "fg2": args.fg2,
        "bg": args.bg or "#0B0F14",
        "glow": not args.no_glow,
        "stroke": args.stroke,
    }
    if args.theme:
        theme = THEMES[args.theme].copy()
        # Theme values are defaults; explicit flags override
        cfg = {**theme, **{k: v for k, v in cfg.items() if v is not None}}

    ascii_text = args.input.read_text(encoding='utf-8')
    svg = build_svg(
        ascii_text,
        fg=cfg["fg"],
        fg2=cfg.get("fg2"),
        bg=cfg["bg"],
        font_family=args.font,
        font_size=args.size,
        line_height=args.line_height,
        glow=cfg.get("glow", True),
        gradient=not args.no_gradient,
        stroke=cfg.get("stroke"),
        stroke_width=args.stroke_width,
        glow_size=args.glow_size,
        animate=args.animate,
        padding=args.padding,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding='utf-8')
    print(f"Wrote {args.output}")


if __name__ == '__main__':
    main()
