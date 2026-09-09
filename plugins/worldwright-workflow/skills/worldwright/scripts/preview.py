"""Copy a local review viewer and serve an output folder on loopback."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil


def prepare(folder):
    folder = Path(folder).resolve()
    if not (folder/'model.glb').is_file():
        raise FileNotFoundError(f'Expected {folder / "model.glb"}; build first.')
    shutil.copytree(Path(__file__).parent/'viewer', folder, dirs_exist_ok=True)
    return folder


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder', type=Path)
    p.add_argument('--port', type=int, default=8770)
    a = p.parse_args()
    try:
        folder = prepare(a.folder)
    except FileNotFoundError as e:
        p.error(str(e))
    server = ThreadingHTTPServer(('127.0.0.1', a.port), partial(SimpleHTTPRequestHandler, directory=str(folder)))
    print(f'Review: http://127.0.0.1:{a.port}/ — Ctrl-C to stop', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
