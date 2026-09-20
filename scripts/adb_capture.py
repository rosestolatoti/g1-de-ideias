#!/usr/bin/env python3
"""
G1 DE IDEIAS — scripts/adb_capture.py
Captura profissional via ADB/Shizuku (moto g84 5G) — integra com pipeline
Usa: adb_self.sh (loopback 127.0.0.1:5555) + termux-api fallback + shizuku rish

Uso:
  python3 scripts/adb_capture.py --check      # verifica adb/shizuku
  python3 scripts/adb_capture.py --screencap  # tira print via adb e salva em prints/original
  python3 scripts/adb_capture.py --watch      # monitora /Screenshots e auto-importa (usado no Termux)
"""
import subprocess, sys, os
from pathlib import Path
import time

BASE = Path(__file__).resolve().parent.parent
ADB_SH = Path("/root/adb_self.sh")
SCREENSHOTS = Path("/storage/emulated/0/Pictures/Screenshots")
ORIGINAL = BASE / "prints" / "original"

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_adb():
    print("🔌 ADB check (adb_self.sh + loopback 127.0.0.1:5555)")
    for cmd in [
        f"bash {ADB_SH} devices",
        f"bash {ADB_SH} shell getprop ro.product.model",
        f"bash {ADB_SH} shell getprop ro.build.version.release",
        "adb devices",
    ]:
        code,out,err = run(cmd)
        print(f"  $ {cmd}\n    -> {out or err} (code {code})")
    # Shizuku
    print("\n🛡️  Shizuku check (rish)")
    for cmd in ["rish -c 'id'", "rish -c 'ls /data/data' 2>&1 | head"]:
        code,out,err = run(cmd)
        print(f"  $ {cmd}\n    -> {(out or err)[:200]} (code {code})")

def screencap():
    ORIGINAL.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    fname = f"Screenshot_{ts}.ADB.png"
    tmp_device = f"/sdcard/Download/00_AMBIENTE_TERMUX/{fname}"
    host_tmp = f"/data/data/com.termux/files/home/{fname}"
    # tenta adb screencap
    print(f"📸 screencap via adb -> {tmp_device}")
    code, out, err = run(f"bash {ADB_SH} shell screencap -p {tmp_device}")
    print(f"  adb screencap: code {code} {out or err}")
    # pull
    time.sleep(0.5)
    # verifica se arquivo existe no device
    code, out, err = run(f"bash {ADB_SH} shell ls -lh {tmp_device}")
    print(f"  ls device: {out or err}")
    if code==0:
        run(f"bash {ADB_SH} pull {tmp_device} {ORIGINAL / fname}")
        print(f"  ✅ pull -> {ORIGINAL / fname}")
        # também copia para Screenshots pra pipeline ver
        try:
            import shutil
            shutil.copy(ORIGINAL / fname, SCREENSHOTS / fname)
            print(f"  ✅ copiado para {SCREENSHOTS / fname}")
        except Exception as e:
            print(f"  ⚠️  copy screenshots falhou: {e}")
        return ORIGINAL / fname
    else:
        print("  ❌ screencap via adb falhou, tentando termux-api fallback")
        code,out,err = run("termux-screenshot -h 2>&1 | head")
        print(f"  termux-screenshot help: {out[:200]}")
        # fallback termux
        tmp2 = f"/data/data/com.termux/files/home/{fname}"
        run(f"termux-screenshot {tmp2}")
        if Path(tmp2).exists():
            import shutil
            shutil.copy(tmp2, ORIGINAL / fname)
            shutil.copy(tmp2, SCREENSHOTS / fname)
            print(f"  ✅ termux-screenshot -> {ORIGINAL / fname}")
            return ORIGINAL / fname
    return None

if __name__ == "__main__":
    if "--check" in sys.argv:
        check_adb()
    elif "--screencap" in sys.argv:
        p = screencap()
        print(f"Resultado: {p}")
    elif "--watch" in sys.argv:
        print(f"👀 watch {SCREENSHOTS} (Ctrl+C pra sair)")
        seen = set(SCREENSHOTS.glob("Screenshot_*"))
        while True:
            current = set(SCREENSHOTS.glob("Screenshot_*"))
            new = current - seen
            for f in new:
                print(f"🆕 novo print: {f.name}")
                # auto crop + ocr pipeline single
                try:
                    import subprocess as sp
                    sp.run([sys.executable, str(BASE/"scripts"/"pipeline.py"), "--limit","1"], check=False)
                except: pass
            seen = current
            time.sleep(2)
    else:
        print(__doc__)
        check_adb()
