#!/usr/bin/env python3
"""Read-only Git integrity check for the frozen ChatGPT baseline."""
import argparse
import csv
import io
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def verify(repo, manifest, ref='HEAD', check_worktree=True):
    anchor = manifest['baseline_commit']
    git(repo, 'cat-file', '-e', anchor + '^{commit}')
    git(repo, 'cat-file', '-e', ref + '^{commit}')
    scope = manifest['protected_prefixes'] + manifest['protected_paths']
    errors = []
    inventory = git(repo, 'ls-tree', '-r', '-z', anchor, '--', *scope)
    entries = [x for x in inventory.split(b'\0') if x]
    if not entries:
        errors.append('empty protected tree')
    tree = {}
    for item in entries:
        meta, path = item.split(b'\t', 1)
        mode, kind, sha = meta.decode('ascii').split()
        tree[path.decode('utf-8', 'surrogateescape')] = sha
    for entry in manifest['reference_blobs'] + manifest['case_packets']:
        if tree.get(entry['path']) != entry['blob']:
            errors.append('anchor blob mismatch: ' + entry['path'])
    diff = git(repo, 'diff', '--name-status', '--no-renames', '-z', anchor, ref, '--', *scope)
    changed = [x.decode('utf-8', 'surrogateescape') for x in diff.split(b'\0') if x]
    if changed:
        errors.append('protected committed tree changed')
    dirty = []
    if check_worktree:
        status = git(repo, 'status', '--porcelain=v1', '-z', '--no-renames',
                     '--untracked-files=all', '--', *scope)
        dirty = [x.decode('utf-8', 'surrogateescape') for x in status.split(b'\0') if x]
        if dirty:
            errors.append('protected worktree/index changed')
    # Compare the baseline CSV to the immutable original role matrix.
    source = git(repo, 'show', anchor + ':index/phase3c_attribute_roles_20261126_v2.csv').decode('utf-8-sig')
    matrix = csv.reader(io.StringIO(source))
    header = next(matrix)
    codes = header[2:]
    role_map = {'D':'선정','I':'선정','A':'판단보류','H':'미선정','P':'미선정','N':'미선정'}
    expected = []
    for queue, event, *roles in matrix:
        if len(roles) != len(codes):
            raise ValueError('matrix width mismatch')
        for code, role in zip(codes, roles):
            expected.append([queue+'-'+code, queue, event, code, role, role_map[role]])
    actual = list(csv.reader(io.StringIO(git(repo, 'show', ref + ':' + manifest['baseline_csv']).decode('utf-8-sig'))))
    if actual != [['review_key','queue_id','event_id','attribute_code','role','chatgpt_review_result']] + expected:
        errors.append('baseline CSV differs from anchored matrix')
    summary = manifest['scope']
    if (len(codes) != summary['attribute_count'] or len(set(codes)) != len(codes)
            or len(expected) != summary['review_rows']
            or len({r[0] for r in expected}) != len(expected)
            or len({r[1] for r in expected}) != summary['case_count']
            or dict(Counter(r[4] for r in expected)) != summary['role_counts']):
        errors.append('baseline counts or keys mismatch')
    return {'status':'FAIL' if errors else 'PASS', 'baseline_commit':anchor,
            'checked_commit':git(repo,'rev-parse',ref).decode().strip(),
            'protected_tree_entries':len(entries), 'reference_blob_checks':len(manifest['reference_blobs']),
            'packet_blob_checks':len(manifest['case_packets']), 'review_rows':len(expected),
            'worktree_checked':check_worktree, 'committed_changes':changed,
            'worktree_changes':dirty, 'errors':errors, 'can_ship':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--manifest', type=Path, help='trusted baseline JSON; defaults to baseline/CHATGPT_BASELINE_V1.json in repo')
    parser.add_argument('--ref', default='HEAD')
    parser.add_argument('--committed-only', action='store_true')
    args = parser.parse_args()
    try:
        path = args.manifest or args.repo / 'baseline/CHATGPT_BASELINE_V1.json'
        manifest = json.loads(path.read_text(encoding='utf-8'))
        result = verify(args.repo, manifest, args.ref, not args.committed_only)
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError) as exc:
        result = {'status':'ERROR', 'errors':[str(exc)], 'can_ship':False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {'PASS':0,'FAIL':1,'ERROR':2}[result['status']]


if __name__ == '__main__':
    sys.exit(main())
