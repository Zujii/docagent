"""Quick environment check: Python, RAM, GPU/VRAM, Ollama + pulled models. Run: python scripts/phase0_check.py"""
import platform
import shutil
import subprocess
import sys

print("Python:", sys.version.split()[0], "| OS:", platform.platform())
try:
    import psutil
    print(f"RAM: {psutil.virtual_memory().total / 2**30:.1f} GB")
except ImportError:
    print("RAM: pip install psutil to show")
if shutil.which("nvidia-smi"):
    out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                         capture_output=True, text=True).stdout.strip()
    print("GPU:", out)
else:
    print("GPU: nvidia-smi not found (CPU-only or drivers missing)")
try:
    import httpx
    r = httpx.get("http://localhost:11434/api/tags", timeout=3)
    models = [m["name"] for m in r.json().get("models", [])]
    print("Ollama: running; models:", models or "none pulled yet")
except Exception as e:  # noqa: BLE001
    print("Ollama: not reachable on :11434 (install/start it).", type(e).__name__)
