"""Open this file in IDLE and select Run > Run Module (F5)."""
from pathlib import Path
import runpy
import sys
import threading
import webbrowser

root = Path(__file__).resolve().parent
sys.argv = [str(root / 'server.py'), '--host', '127.0.0.1', '--port', '8000']
threading.Timer(1.0, lambda: webbrowser.open('http://127.0.0.1:8000')).start()
print('Starting Python Practice. Keep this IDLE window open.', flush=True)
runpy.run_path(str(root / 'server.py'), run_name='__main__')
