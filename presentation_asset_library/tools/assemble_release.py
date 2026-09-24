"""Import an exact presentation and its exported media into an archival release.

This importer never edits a PowerPoint or overwrites differing release files.
Run against the original project; ordinary library use needs no Python.
"""
from pathlib import Path
import argparse, csv, hashlib, io, json, posixpath, re, shutil, zipfile
from urllib.parse import unquote
from xml.etree import ElementTree as E

LIB = Path(__file__).resolve().parents[1]
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'rel':'http://schemas.openxmlformats.org/package/2006/relationships',
      's':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(data): return hashlib.sha256(data).hexdigest()
def store(dest, data):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if sha(dest.read_bytes()) != sha(data):
            raise RuntimeError(f'Release file differs; use a new release directory: {dest}')
    else: dest.write_bytes(data)
    return dest.relative_to(LIB).as_posix()
def jsonbytes(obj): return (json.dumps(obj, indent=2, ensure_ascii=False)+'\n').encode('utf-8')
def target(part, name):
    name=unquote(name)
    return posixpath.normpath(name.lstrip('/') if name.startswith('/') else posixpath.join(posixpath.dirname(part), name))
def relationships(pkg, part):
    rp=posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part)+'.rels')
    return {r.get('Id'):r for r in E.fromstring(pkg[rp])} if rp in pkg else {}
def paragraphs(node):
    return [''.join(p.itertext()) for p in node.findall('.//a:p', NS)]
def export_workbook(data, dest):
    """Keep original XLSX plus literal worksheet values as UTF-8 CSV."""
    with zipfile.ZipFile(io.BytesIO(data)) as wb:
        shared=[]
        if 'xl/sharedStrings.xml' in wb.namelist():
            shared=[''.join(s.itertext()) for s in E.fromstring(wb.read('xl/sharedStrings.xml'))]
        for sheet in sorted(n for n in wb.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+.xml', n)):
            rows=[]
            for row in E.fromstring(wb.read(sheet)).findall('.//s:row', NS):
                vals=[]
                for c in row.findall('s:c', NS):
                    letters=re.match('[A-Z]+', c.get('r','A1')).group()
                    col=0
                    for char in letters: col=col*26+ord(char)-64
                    while len(vals)<col: vals.append('')
                    v=c.find('s:v', NS); value=v.text if v is not None else ''
                    if c.get('t')=='s' and value: value=shared[int(value)]
                    elif c.get('t')=='inlineStr': value=''.join(c.find('s:is',NS).itertext())
                    vals[col-1]=value
                rows.append(vals)
            output=io.StringIO(newline=''); csv.writer(output).writerows(rows)
            store(dest/Path(sheet).with_suffix('.csv').name, output.getvalue().encode('utf-8'))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--release', default='2026-09-10_v9')
    ap.add_argument('--deck', default='output/presentations/Oriented_Powder_8min_Animated_v9.pptx')
    ap.add_argument('--expected-sha256', default='0feca65d8e57c764666012cc75cd880da660fd1fea12eedba0cec69193c2cec3')
    args=ap.parse_args(); root=args.project.resolve(); rel=LIB/'releases'/args.release
    deck=root/args.deck; raw=deck.read_bytes()
    assert sha(raw)==args.expected_sha256, 'The requested final deck hash does not match.'
    deckpath=store(rel/'presentation'/deck.name,raw)
    imports=[]
    def copy(src, dest, role):
        data=src.read_bytes(); p=store(dest,data)
        imports.append({'path':p,'original_path':str(src.resolve()),'sha256':sha(data),'bytes':len(data),'role':role})
        return p
    for folder in ['animations','figures','interactive']:
        for p in sorted((root/'output/presentations'/folder).glob('*')):
            if p.is_file(): copy(p,rel/'assets'/folder/p.name, 'exported_'+folder)
    # Final image crops not present among the standalone public figures.
    for folder, dest, patterns in [
        ('animated_deck_v9/figures/se_retained','Bi2Se3_profiles',['*.png']),
        ('animated_deck_v7/diagnostics','Bi2Te3_profiles',['te_*.png']),
        ('animated_deck_v8/ordered_render/bi2se3','Bi2Se3_detector',['*.png']),
        ('animated_deck_v8/ordered_render/bi2te3','Bi2Te3_detector',['*.png'])]:
        for pattern in patterns:
            for p in sorted((root/'build_codex/slate_talk'/folder).glob(pattern)):
                copy(p,rel/'assets'/'figures'/dest/p.name, 'final_figure_panel')
    for p in sorted((root/'build_codex/slate_talk/animated_deck_v9/final_renders').glob('slide-*.png')):
        if re.fullmatch(r'slide-\d{2}\.png',p.name): copy(p,rel/'slides'/p.name,'verified_slide_render')
    receipts=['final_validation_verified.json','final_sdk_validation.json','final_visual_review.private.json',
        'candidate_independent_audit.private.json','candidate_media_editability_audit.private.json',
        'final_independent_pixel_review.private.json','chart_cache_precision_audit.private.json',
        'se_final_arrays_review.private.json','se_retained_selection_review.private.json']
    for name in receipts:
        p=root/'build_codex/slate_talk/animated_deck_v9'/name
        if p.exists(): copy(p,rel/'provenance'/'deck_validation'/name,'historical_validation_receipt')
    with zipfile.ZipFile(io.BytesIO(raw)) as z: pkg={n:z.read(n) for n in z.namelist()}
    presentation=E.fromstring(pkg['ppt/presentation.xml'])
    prels=relationships(pkg,'ppt/presentation.xml')
    order=[target('ppt/presentation.xml',prels[s.get('{'+NS['r']+'}id')].get('Target')) for s in presentation.find('p:sldIdLst',NS)]
    slides=[]; media={}
    for number,part in enumerate(order,1):
        xml=E.fromstring(pkg[part]); rlist=relationships(pkg,part)
        texts=[''.join(t.text or '' for t in p.findall('.//a:t',NS)) for p in xml.findall('.//a:p',NS)]
        texts=[t for t in texts if t.strip()]; hidden=xml.get('show')=='0'
        notes=''; members=[]; charts=[]; tables=[]
        for r in rlist.values():
            if r.get('TargetMode')=='External': continue
            path=target(part,r.get('Target'))
            if path.startswith('ppt/media/'):
                out=store(rel/'assets'/'deck_embedded'/Path(path).name,pkg[path])
                m=media.setdefault(path,{'part':path,'path':out,'sha256':sha(pkg[path]),'bytes':len(pkg[path]),'slides':[]})
                if number not in m['slides']: m['slides'].append(number)
                if out not in members: members.append(out)
            elif r.get('Type','').endswith('/notesSlide'):
                n=E.fromstring(pkg[path]); body=[]
                for sp in n.findall('.//p:sp',NS):
                    ph=sp.find('p:nvSpPr/p:nvPr/p:ph',NS)
                    if ph is not None and ph.get('type')=='body':
                        body+=[''.join(t.text or '' for t in p.findall('.//a:t',NS)) for p in sp.findall('.//a:p',NS)]
                notes='\n'.join(body)
            elif r.get('Type','').endswith('/chart'): charts.append(path)
        for ti,tbl in enumerate(xml.findall('.//a:tbl',NS),1):
            values=[[''.join(t.text or '' for t in c.findall('.//a:t',NS)) for c in tr.findall('a:tc',NS)] for tr in tbl.findall('a:tr',NS)]
            sio=io.StringIO(newline=''); csv.writer(sio).writerows(values)
            tables.append(store(rel/'data'/'native_tables'/f'slide-{number:02d}-table-{ti}.csv',sio.getvalue().encode('utf-8')))
        notespath=store(rel/'slides'/f'slide-{number:02d}-notes.txt',(notes+'\n').encode('utf-8'))
        slides.append({'number':number,'title':texts[0] if texts else f'Slide {number}','texts':texts,'hidden':hidden,
            'part':part,'preview':(rel/'slides'/f'slide-{number:02d}.png').relative_to(LIB).as_posix(),
            'notes_path':notespath,'media_paths':members,'chart_parts':charts,'table_paths':tables,'asset_ids':[]})
    chart_index=[]
    for part,data in pkg.items():
        if part.startswith('ppt/charts/') or part.startswith('ppt/embeddings/'):
            store(rel/'data'/'native_chart_packages'/part,data)
            if part.endswith('.xlsx'): export_workbook(data,rel/'data'/'native_chart_csv'/Path(part).stem)
        if re.fullmatch(r'ppt/charts/chart\d+\.xml',part):
            chart_xml=E.fromstring(data)
            books=[]
            for r in relationships(pkg,part).values():
                if r.get('TargetMode')=='External':continue
                t=target(part,r.get('Target'))
                if t.endswith('.xlsx'):
                    books.append({'xlsx':(rel/'data/native_chart_packages'/t).relative_to(LIB).as_posix(),
                        'csv_directory':(rel/'data/native_chart_csv'/Path(t).stem).relative_to(LIB).as_posix()})
            chart_index.append({'part':part,'slides':[s['number'] for s in slides if part in s['chart_parts']],
                'archived_xml':(rel/'data/native_chart_packages'/part).relative_to(LIB).as_posix(),
                'workbooks':books,'chart_text':[t.text for t in chart_xml.findall('.//a:t',NS)]})
    store(rel/'data/native_chart_index.json',jsonbytes(chart_index))
    assert len(slides)==25 and not any(s['hidden'] for s in slides)
    index={'schema_version':1,'release_id':args.release,
        'presentation':{'path':deckpath,'sha256':sha(raw),'bytes':len(raw),'slide_count':len(slides)},
        'slides':slides,'embedded_media':list(media.values()),'imports':imports}
    # The importer manifest is generated metadata; it may be refreshed while assembling this release.
    dest=rel/'provenance'/'import_manifest.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(jsonbytes(index))
    print(json.dumps({'deck':deckpath,'deck_sha256':sha(raw),'slides':len(slides),'embedded_assets':len(media),'imports':len(imports)},indent=2))
if __name__=='__main__': main()
