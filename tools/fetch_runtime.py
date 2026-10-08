from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
root = Path(__file__).resolve().parents[1] / 'web/vendor'
root.mkdir(exist_ok=True)
def fetch(asset):
    with urlopen('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/' + asset, timeout=90) as r:
        data = r.read()
    (root / asset).write_bytes(data)
    print(asset, len(data), flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(fetch, ['pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']))
