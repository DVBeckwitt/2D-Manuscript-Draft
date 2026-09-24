"""Create and verify the portable cylinder-bridge ZIP."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                 and p.suffix!='.pyc' and p.name not in {'file_manifest.json','SHA256SUMS.txt'})
    rec=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
    m=ROOT/'file_manifest.json'
    m.write_text(json.dumps({'name':'Cylinder bridge v3','date':'2026-09-11',
         'description':'Near-delta finite peaks, smooth accelerating broadening, azimuthal cylinder, mosaic tilts and exact Ewald selection.',
         'scope':'Static figure, 26-second animation, local source/data, captions and verification.',
         'scientific_status':'Illustrative finite-stack geometry; not a new fit or detector-count prediction.',
         'files':rec},indent=2)+'\n',encoding='utf-8')
    checks=rec+[{'path':m.name,'sha256':sha(m)}]
    sm=ROOT/'SHA256SUMS.txt'
    sm.write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in checks),encoding='utf-8')
    zpath=ROOT.parent/'Cylinder_Bridge_v3.zip'
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths+[m,sm]:z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        for r in checks:assert hashlib.sha256(z.read(ROOT.name+'/'+r['path'])).hexdigest()==r['sha256'],r['path']
    report={'status':'PASS','zip':zpath.name,'bytes':zpath.stat().st_size,'sha256':sha(zpath),
            'file_count':len(paths)+2,'verified_hashes':len(checks),'zip_crc':'PASS'}
    zpath.with_suffix('.zip.sha256').write_text(report['sha256']+'  '+zpath.name+'\n',encoding='utf-8')
    zpath.with_suffix('.zip.verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
