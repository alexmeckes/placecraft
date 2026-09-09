"""Run an explicitly selected Python builder inside Blender; no shell interpolation."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess


def find_blender(explicit=None):
    requested = explicit or os.environ.get('BLENDER')
    if requested:
        found = shutil.which(requested) or (requested if Path(requested).is_file() else None)
        if not found:
            raise FileNotFoundError(f'Blender executable not found: {requested}')
        return str(found)
    found = shutil.which('blender')
    if found:
        return found
    mac = Path('/Applications/Blender.app/Contents/MacOS/Blender')
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError('Install Blender and set BLENDER to its executable, or pass --blender.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blender')
    p.add_argument('builder', type=Path)
    p.add_argument('arguments', nargs=argparse.REMAINDER)
    a = p.parse_args()
    builder = a.builder.resolve()
    if not builder.is_file():
        p.error(f'Builder not found: {builder}')
    tail = a.arguments[1:] if a.arguments[:1] == ['--'] else a.arguments
    try:
        executable = find_blender(a.blender)
    except FileNotFoundError as e:
        p.error(str(e))
    return subprocess.call([executable, '--background', '--factory-startup',
                            '--python-exit-code', '1', '--python', str(builder), '--', *tail])


if __name__ == '__main__':
    raise SystemExit(main())
