#!/usr/bin/env python3
"""Strip the language pie chart and the contribution radar (hexagon) chart out of
the SVGs produced by github-profile-3d-contrib, keeping only the isometric
calendar. The action has no option for this, so we cut the two panel groups.

Panel groups are the only ones using comma-separated translate() coordinates
(`translate(40, 520)`), while calendar cells use `translate(140 154.18)`.
"""
import re
import sys

PANEL = re.compile(r'<g transform="translate\([0-9.]+, [0-9.]+\)"[^>]*>')
TAG = re.compile(r"<(/?)g\b[^>]*?(/?)>")


def cut_group(svg: str, start: int) -> str:
    """Remove the <g> starting at `start` and everything up to its matching </g>."""
    depth = 0
    for m in TAG.finditer(svg, start):
        closing, self_closing = m.groups()
        if self_closing:
            continue
        depth += -1 if closing else 1
        if depth == 0:
            return svg[:start] + svg[m.end():]
    raise ValueError(f"unbalanced <g> at offset {start}")


def strip(svg: str) -> str:
    while (m := PANEL.search(svg)) is not None:
        svg = cut_group(svg, m.start())
    return svg


def main(paths: list[str]) -> None:
    for path in paths:
        with open(path, encoding="utf-8") as f:
            svg = f.read()
        out = strip(svg)
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"{path}: {len(svg) - len(out)} bytes removed")


def demo() -> None:
    src = (
        '<svg><g transform="translate(1 2)"><rect/></g>'
        '<g transform="translate(40, 520)"><g><path d="keep-me-not"/></g></g>'
        '<text>tail</text></svg>'
    )
    out = strip(src)
    assert "translate(40, 520)" not in out, out
    assert "keep-me-not" not in out, out
    assert 'translate(1 2)' in out and "<text>tail</text>" in out, out
    print("demo ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--demo"]:
        demo()
    else:
        main(sys.argv[1:])
