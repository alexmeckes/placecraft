"""Convenience commands for the self-contained skill example."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/placecraft/skills/placecraft'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    b = sub.add_parser('build')
    b.add_argument('--stage', choices=['massing', 'construction', 'finish'], default='finish')
    b.add_argument('--render', action='store_true')
    b.add_argument('--seed', type=int, default=23)
    b.add_argument('--pass', dest='pass_number', type=int, choices=[1, 2], default=2)
    b.add_argument('--out', type=Path, default=ROOT/'out/kiln-shelter')
    b.add_argument('--blender')
    c = sub.add_parser('check')
    c.add_argument('--out', type=Path, default=ROOT/'out/kiln-shelter')
    c.add_argument('--compare', type=Path)
    s = sub.add_parser('serve')
    s.add_argument('--out', type=Path, default=ROOT/'out/kiln-shelter')
    s.add_argument('--port', type=int, default=8770)
    a = p.parse_args()
    scripts = SKILL/'scripts'
    if a.command == 'build':
        cmd = [sys.executable, str(scripts/'run.py')]
        if a.blender:
            cmd += ['--blender', a.blender]
        cmd += [str(SKILL/'assets/kiln-shelter/build.py'), '--', '--out', str(a.out.resolve()),
                '--stage', a.stage, '--seed', str(a.seed), '--pass', str(a.pass_number)]
        if a.render:
            cmd += ['--render']
    elif a.command == 'check':
        cmd = [sys.executable, str(scripts/'check_glb.py'), str(a.out/'model.glb')]
        if a.compare:
            cmd += ['--compare', str(a.compare/'model.glb')]
    else:
        cmd = [sys.executable, str(scripts/'preview.py'), str(a.out), '--port', str(a.port)]
    return subprocess.call(cmd)


if __name__ == '__main__':
    raise SystemExit(main())
