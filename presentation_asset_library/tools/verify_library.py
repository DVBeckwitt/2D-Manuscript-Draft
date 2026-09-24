"""Verify an extracted library against SHA256SUMS.txt using Python 3 only."""
from pathlib import Path
import argparse, hashlib, json, sys

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as src:
        for block in iter(lambda:src.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()

def verify(root):
    root=root.resolve(); failures=[]; checked=0
    sums=root/'SHA256SUMS.txt'
    if not sums.is_file(): return {'ok':False,'checked':0,'failures':['SHA256SUMS.txt is missing']}
    seen=set()
    for line in sums.read_text(encoding='utf-8').splitlines():
        if not line: continue
        expected, name=line.split('  ',1)
        p=root/name
        if name in seen or len(expected)!=64 or not p.resolve().is_relative_to(root):
            failures.append(f'Unsafe or duplicate manifest entry: {name}'); continue
        seen.add(name)
        if not p.is_file(): failures.append(f'Missing: {name}')
        elif digest(p)!=expected: failures.append(f'Changed: {name}')
        checked+=1
    return {'ok':not failures,'checked':checked,'failures':failures,
            'scope':'Every listed archive file; SHA256SUMS.txt is anchored by the external ZIP checksum.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root',type=Path,nargs='?',default=Path(__file__).resolve().parents[1])
    args=ap.parse_args(); result=verify(args.root)
    print(json.dumps(result,indent=2));sys.exit(0 if result['ok'] else 1)
if __name__=='__main__': main()
