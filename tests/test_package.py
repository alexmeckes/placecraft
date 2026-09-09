import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'plugins/placecraft/skills/placecraft'


class PackageTests(unittest.TestCase):
    def test_markdown_relative_links_resolve(self):
        failures=[]
        for path in ROOT.rglob('*.md'):
            if any(part in {'out','.git','node_modules'} for part in path.relative_to(ROOT).parts):continue
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' in target or target.startswith('#'):continue
                target=target.split('#')[0]
                if not (path.parent/target).exists():failures.append(f'{path.relative_to(ROOT)} -> {target}')
        self.assertEqual(failures,[])

    def test_installed_skill_resources_are_self_contained(self):
        for path in SKILL.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' in target or target.startswith('#'):continue
                self.assertTrue((path.parent/target.split('#')[0]).resolve().is_relative_to(SKILL.resolve()))

    def test_provenance_hashes_match(self):
        for item in json.loads((ROOT/'docs/media-provenance.json').read_text())['media']:
            self.assertEqual(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest(),item['sha256'])

    def test_manifest_and_marketplace_resolve(self):
        m=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text())
        for entry in m['plugins']:
            plugin=ROOT/entry['source']['path']
            manifest=json.loads((plugin/'.codex-plugin/plugin.json').read_text())
            self.assertEqual(manifest['name'],plugin.name)
            self.assertTrue((plugin/manifest['skills']/'placecraft/SKILL.md').is_file())

if __name__=='__main__':unittest.main()
