#!/usr/bin/env bash
set -euo pipefail
cd /workspace/python-practice1
mkdir -p .local
if ! curl --fail --silent http://127.0.0.1:8000/ -o .local/ready-index.html; then
  nohup python3 server.py --port 8000 > .local/server.log 2>&1 &
  echo "$!" > .local/server.pid
fi
for practice_attempt in {1..10}; do
  if curl --fail --silent http://127.0.0.1:8000/ -o .local/ready-index.html; then
    python3 - <<'PY'
import json
from pathlib import Path
from urllib.request import urlopen
html=Path('.local/ready-index.html').read_text()
assert 'Python 小步练习室' in html, 'Port 8000 is serving another application; do not stop it blindly.'
with urlopen('http://127.0.0.1:8000/content.json', timeout=5) as r:
    content=json.load(r)
assert len(content['questions'])==100
assert len(content['mapping'])==10
print('Ready: Python Practice on port 8000; 100 exercises and 10 original mappings.')
PY
    exit 0
  fi
  sleep 1
done
cat .local/server.log
exit 1
