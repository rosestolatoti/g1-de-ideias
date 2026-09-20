#!/usr/bin/env python3
"""
G1 DE IDEIAS — app/services/ocr_service.py
OCR profissional via Tesseract 5.5.0 por+eng --psm 6
"""
import subprocess
import logging
from pathlib import Path
import os
import time

log = logging.getLogger("g1.ocr")

def ocr_image(image_path: Path, lang="por+eng", psm=6, timeout=20) -> str:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"OCR: arquivo não existe {image_path}")
    env = dict(os.environ, OMP_THREAD_LIMIT="2")
    try:
        # tenta via arquivo (mais estável que stdout)
        tmp = f"/tmp/ocr_{image_path.stem}_{os.getpid()}"
        cmd = ["timeout", str(timeout), "tesseract", str(image_path), tmp, "-l", lang, "--psm", str(psm), "--oem", "1"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5, env=env)
        txt_path = Path(tmp + ".txt")
        text = ""
        if txt_path.exists():
            text = txt_path.read_text(encoding="utf-8", errors="ignore").strip()
            txt_path.unlink(missing_ok=True)
        # fallback stdout se arquivo vazio
        if not text:
            cmd2 = ["timeout", str(timeout), "tesseract", str(image_path), "stdout", "-l", lang, "--psm", str(psm), "--oem", "1"]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=timeout+5, env=env)
            text = result2.stdout.strip()
            if not text and Path(tmp + ".txt").exists():
                text = Path(tmp + ".txt").read_text(encoding="utf-8", errors="ignore").strip()
        # limpeza
        text = " ".join(text.split())
        return text[:5000]
    except subprocess.TimeoutExpired:
        log.warning(f"OCR timeout {image_path}")
        return ""
    except Exception as e:
        log.warning(f"OCR erro {image_path}: {e}")
        return ""

def ocr_batch(files, lang="por+eng"):
    out = []
    for f in files:
        txt = ocr_image(Path(f), lang=lang)
        out.append((Path(f), txt))
        time.sleep(0.15)  # respira CPU
    return out
