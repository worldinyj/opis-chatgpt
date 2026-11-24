#!/usr/bin/env python3
"""Import the pinned V02 archive without modifying any original byte."""
import argparse, hashlib, json, pathlib, zipfile
ROOT = 'incident-video-starter-20261030-v02'
PIN = 'd4fcd9f11703c756d8566f66e56866dc3f06c8f019ef7c5d1885df9a7b3e2483'
def digest(data):
    return hashlib.sha256(data).hexdigest()
def run(archive, repo, check_only=False):
    archive = pathlib.Path(archive)
    if digest(archive.read_bytes()) != PIN:
        raise ValueError('ZIP SHA-256 mismatch')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or any(not n.startswith(ROOT + '/') or '..' in pathlib.PurePosixPath(n).parts or '\\' in n for n in names):
            raise ValueError('unsafe or duplicate ZIP member')
        manifest_path = ROOT + '/BUNDLE_MANIFEST.json'
        manifest = json.loads(z.read(manifest_path))
        expected = {ROOT + '/' + x['file']: x for x in manifest['files']}
        if len(expected) != 25 or set(names) != set(expected) | {manifest_path}:
            raise ValueError('unexpected file set')
        data = {n: z.read(n) for n in names}
        for n, x in expected.items():
            if len(data[n]) != x['bytes'] or digest(data[n]) != x['sha256']:
                raise ValueError('manifest mismatch: ' + n)
    target = pathlib.Path(repo).resolve() / 'video' / 'upstream'
    for n, content in data.items():
        p = target / n
        if not p.resolve().is_relative_to(target.resolve()):
            raise ValueError('unsafe destination: ' + n)
        if p.exists() and (not p.is_file() or p.read_bytes() != content):
            raise ValueError('refusing overwrite: ' + n)
    if not check_only:
        for n, content in data.items():
            p = target / n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(content)
        assert all((target / n).read_bytes() == content for n, content in data.items())
    print(f'ZIP PASS; manifest 25/25; {len(data)} original files; ' + ('check only' if check_only else 'imported and reread'))
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('archive')
    p.add_argument('--repo', default='.')
    p.add_argument('--check-only', action='store_true')
    args = p.parse_args()
    run(args.archive, args.repo, args.check_only)
