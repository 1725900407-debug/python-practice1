"""Open in IDLE, then select Run > Run Module (F5). No extra packages."""
from pathlib import Path
import importlib.util
import threading
import webbrowser

root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('practice_static_server', root / 'server.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# Select a free local port instead of conflicting with another running program.
server = module.ThreadingHTTPServer(('127.0.0.1', 0), module.Handler)
address = f'http://127.0.0.1:{server.server_address[1]}'
print(f'Practice website: {address}', flush=True)
print('Keep IDLE open. To stop the website, press Control+C in the Shell.', flush=True)
threading.Timer(0.5, lambda: webbrowser.open(address)).start()
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
