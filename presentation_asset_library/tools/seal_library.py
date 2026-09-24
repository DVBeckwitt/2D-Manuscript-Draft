"""Write SHA-256 inventories and a ZIP64 snapshot, then verify every ZIP member.

Use once after completing and checking a new release. Existing ZIPs are never
overwritten. The ZIP destination must be outside the library being packaged.
"""
from pathlib import Path
import argparse, hashlib, json, zipfile
from verify_library import digest, verify

ROOT=Path(__file__).resolve().parents[1]
def candidates():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and
        '__pycache__' not in p.parts and p not in [ROOT/'SHA256SUMS.txt',ROOT/'FILES.json'])

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--zip',type=Path)
    group.add_argument('--inventory-only',action='store_true',help='Refresh manifests without making a ZIP')
    args=ap.parse_args(); out=args.zip.resolve() if args.zip else None
    if out and out.is_relative_to(ROOT): raise SystemExit('ZIP must be outside the library.')
    if out and out.exists(): raise SystemExit('ZIP already exists. Use a new snapshot filename.')
    entries=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in candidates()]
    (ROOT/'FILES.json').write_text(json.dumps({'schema_version':1,'files':entries},indent=2)+'\n',encoding='utf-8')
    allpaths=candidates()+[ROOT/'FILES.json']
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in sorted(allpaths)),encoding='utf-8')
    check=verify(ROOT)
    if not check['ok']: raise SystemExit(json.dumps(check))
    if args.inventory_only:
        print(json.dumps(check,indent=2));return
    allpaths.append(ROOT/'SHA256SUMS.txt')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(allpaths): z.write(p,'presentation_asset_library/'+p.relative_to(ROOT).as_posix())
    # Read decompressed bytes, not merely ZIP metadata or CRC values.
    failures=[]
    with zipfile.ZipFile(out) as z:
        for p in allpaths:
            name='presentation_asset_library/'+p.relative_to(ROOT).as_posix()
            h=hashlib.sha256()
            with z.open(name) as src:
                for block in iter(lambda:src.read(4*1024*1024),b''): h.update(block)
            if h.hexdigest()!=digest(p): failures.append(name)
    if failures: raise SystemExit('ZIP verification failed: '+str(failures))
    checksum=digest(out)
    out.with_suffix(out.suffix+'.sha256').write_text(f'{checksum}  {out.name}\n',encoding='utf-8')
    print(json.dumps({'ok':True,'files':len(allpaths),'zip':str(out),'zip_bytes':out.stat().st_size,'zip_sha256':checksum},indent=2))
if __name__=='__main__': main()
