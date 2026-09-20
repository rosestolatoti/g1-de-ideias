#!/usr/bin/env python3
"""
G1 DE IDEIAS — app/services/crop_service.py
Crop profissional da barra de notificação (moto g84 5G 1080x2400)
Padrão: top 110px (DisplayCutout 106 + margem) + bottom 48px (gesture nav)
"""
from pathlib import Path
from PIL import Image
import logging

log = logging.getLogger("g1.crop")

DEFAULT_TOP = 110
DEFAULT_BOTTOM = 48
DEFAULT_QUALITY = 92

def crop_image(input_path: Path, output_path: Path, top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM, quality=DEFAULT_QUALITY):
    input_path = Path(input_path)
    output_path = Path(output_path)
    im = Image.open(input_path)
    w, h = im.size
    left, upper, right, lower = 0, top, w, h - bottom
    if lower <= upper:
        raise ValueError(f"Crop inválido: {w}x{h} com top={top} bottom={bottom}")
    cropped = im.crop((left, upper, right, lower))
    if cropped.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", cropped.size, (255, 255, 255))
        bg.paste(cropped, mask=cropped.split()[-1])
        cropped = bg
    elif cropped.mode != "RGB":
        cropped = cropped.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path, quality=quality, optimize=True)
    log.info(f"crop {input_path.name} {w}x{h} -> {cropped.size} (top {top}+bottom {bottom})")
    return cropped.size

def batch_crop(files, output_dir: Path, top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM):
    output_dir = Path(output_dir)
    ok = 0
    for f in files:
        try:
            f = Path(f)
            out = output_dir / f.name.replace(".png",".jpg").replace(".PNG",".jpg")
            crop_image(f, out, top=top, bottom=bottom)
            ok += 1
        except Exception as e:
            log.warning(f"crop fail {f}: {e}")
    return ok
