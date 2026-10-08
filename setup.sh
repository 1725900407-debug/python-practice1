#!/usr/bin/env bash
set -euo pipefail
cd /workspace/python-practice1
mkdir -p web/vendor
for asset in pyodide.js pyodide.asm.js pyodide.asm.wasm python_stdlib.zip pyodide-lock.json; do
  if [ ! -s "web/vendor/$asset" ]; then
    curl --fail --location --retry 2 --max-time 120 "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/$asset" -o "web/vendor/$asset.tmp"
    mv "web/vendor/$asset.tmp" "web/vendor/$asset"
  fi
done
sha256sum --check runtime.sha256
python3 tools/build_content.py
python3 -m unittest discover -s tests -v
