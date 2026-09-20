#!/usr/bin/env python3
"""
G1 DE IDEIAS — crop_prints.py
Corta barra de notificação (hora, wifi, bateria, 5G) e barra de navegação dos prints.

Padrão Moto g84 5G 1080x2400:
  - DisplayCutout top: 106px (confirmado via dumpsys: Rect(0,106))
  - Navigation bar bottom: ~48px (gesto) a 134px (3 botões)
  Padrão adotado: top=110, bottom=48 (conservador, não corta conteúdo do app)

Uso:
  python3 scripts/crop_prints.py --all
  python3 scripts/crop_prints.py --input prints/original/*.png --output prints/cropped/
  python3 scripts/crop_prints.py --file /storage/emulated/0/Pictures/Screenshots/Screenshot_20260910-205937.X.png
"""
import argparse
import json
from pathlib import Path
from PIL import Image

# Config padrão
DEFAULT_TOP = 110      # corta status bar + cutout
DEFAULT_BOTTOM = 48    # corta gesture nav (se 3 botões, use 134)
DEFAULT_WIDTH = 1080   # largura padrão

def crop_image(input_path: Path, output_path: Path, top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM, quality=92):
    im = Image.open(input_path)
    w, h = im.size
    # Calcula área de crop
    left, upper, right, lower = 0, top, w, h - bottom
    if lower <= upper:
        raise ValueError(f"Crop inválido: {w}x{h} com top={top} bottom={bottom}")
    cropped = im.crop((left, upper, right, lower))
    # Converte RGBA -> RGB se necessário (JPG não suporta alpha)
    if cropped.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", cropped.size, (255, 255, 255))
        bg.paste(cropped, mask=cropped.split()[-1])
        cropped = bg
    elif cropped.mode != "RGB":
        cropped = cropped.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path, quality=quality)
    return cropped.size, (top, bottom)

def main():
    parser = argparse.ArgumentParser(description="Crop barra notificação dos prints G1 DE IDEIAS")
    parser.add_argument("--all", action="store_true", help="Processa todos de data/noticias.json")
    parser.add_argument("--input", nargs="*", help="Arquivos de entrada (glob)")
    parser.add_argument("--file", help="Um arquivo específico")
    parser.add_argument("--output", help="Pasta de saída (default prints/cropped/)")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, help=f"Pixels a cortar no topo (default {DEFAULT_TOP})")
    parser.add_argument("--bottom", type=int, default=DEFAULT_BOTTOM, help=f"Pixels a cortar embaixo (default {DEFAULT_BOTTOM})")
    parser.add_argument("--quality", type=int, default=92)
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    json_path = base / "data" / "noticias.json"
    orig_dir = Path("/storage/emulated/0/Pictures/Screenshots")
    cropped_dir = Path(args.output) if args.output else base / "prints" / "cropped"
    
    files = []
    if args.all:
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            for n in data.get("noticias", []) + data.get("ideias", []):
                # tenta achar arquivo original
                img = n.get("imagem_original") or n.get("imagem") or ""
                fname = Path(img).name
                f = orig_dir / fname
                if f.exists():
                    files.append(f)
                else:
                    # tenta templates/prints
                    alt = base / "prints" / "original" / fname
                    if alt.exists():
                        files.append(alt)
            print(f"Modo --all: {len(files)} arquivos do JSON")
        else:
            # fallback: todos da pasta Screenshots
            files = sorted(orig_dir.glob("Screenshot_*.png"))
            print(f"JSON não encontrado, usando {len(files)} da pasta Screenshots")
    elif args.file:
        files = [Path(args.file)]
    elif args.input:
        for pattern in args.input:
            files.extend(Path().glob(pattern))
        # também tenta expandir manualmente se glob não funcionou
        if not files:
            import glob
            for pat in args.input:
                files.extend([Path(p) for p in glob.glob(pat)])
    else:
        # default: 10 últimos
        files = sorted(orig_dir.glob("Screenshot_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
        print(f"Sem args, pegando 10 últimos de {orig_dir}")

    if not files:
        print("Nenhum arquivo encontrado. Use --all ou --file")
        return

    ok = 0
    for f in files:
        try:
            out = cropped_dir / f.name.replace(".png", ".jpg").replace(".PNG", ".jpg")
            # mantém .png se quiser, mas JPG é menor
            new_size, (t,b) = crop_image(f, out, top=args.top, bottom=args.bottom, quality=args.quality)
            print(f"✓ {f.name} {Image.open(f).size} → {new_size} (top {t}+bottom {b}) → {out}")
            ok += 1
        except Exception as e:
            print(f"✗ {f.name}: {e}")
    print(f"\nFeito: {ok}/{len(files)} em {cropped_dir}")
    print(f"Padrão: top={args.top}px (barra hora/wifi) + bottom={args.bottom}px (nav) → sem notificação, pronto pro Globo")

if __name__ == "__main__":
    main()
