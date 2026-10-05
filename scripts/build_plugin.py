#!/usr/bin/env python3
"""Build a submission ZIP from an explicit list of distributable files."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'plugin.json', 'README.md', 'LICENSE', 'CHANGELOG.md', 'PRIVACY.md',
    'assets/icon.svg', 'examples/guide-example.md',
    'skills/voice-kit/SKILL.md',
    'skills/voice-kit/prompts/analysis.md',
    'skills/voice-kit/references/detox-core.md',
    'skills/voice-kit/references/storage.md',
    'skills/voice-kit/scripts/extract.py',
    'skills/voice-kit/scripts/split.py',
    'skills/voice-kit/templates/voice-guide.md',
    'skills/voice-kit/templates/formats/dm.md',
    'skills/voice-kit/templates/formats/email.md',
    'skills/voice-kit/templates/formats/linkedin.md',
    'skills/voice-kit/templates/formats/x.md',
    'skills/voice-kit/workflows/build.md',
    'skills/voice-kit/workflows/refresh.md',
    'skills/voice-kit/workflows/write.md',
)


def main():
    manifest = json.loads((ROOT / 'plugin.json').read_text())
    for name in FILES:
        path = ROOT / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f'Invalid distribution file: {name}')
    interface = manifest['extensions']['com.openai']['interface']
    for key, limit in [('displayName', 30), ('shortDescription', 30), ('longDescription', 4000), ('developerName', 80)]:
        assert 0 < len(interface[key]) <= limit, key
    for key in ('logo', 'composerIcon'):
        assert interface[key].removeprefix('./') in FILES, key
    version = manifest['version']
    assert all(part.isdigit() for part in version.split('.')) and len(version.split('.')) == 3
    out = ROOT / 'dist' / f'voice-kit-{version}.zip'
    out.parent.mkdir(exist_ok=True)
    with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(ROOT / name, name)
    with ZipFile(out) as archive:
        assert set(archive.namelist()) == set(FILES)
        assert archive.testzip() is None
    print(f'{out} ({len(FILES)} files)')


if __name__ == '__main__':
    main()
