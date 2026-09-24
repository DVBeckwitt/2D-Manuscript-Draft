"""Resolve curated asset families against locally archived files.

Run after assemble_release.py and the source snapshot. Missing curated exports
are reported, never silently represented as reproducible or included.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess

LIB=Path(__file__).resolve().parents[1]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def pathkey(p):return str(p).replace('\\','/').lower()
def prose(value):
    if isinstance(value,list):return [prose(v) for v in value]
    if not value:return value
    value=re.sub(r'\b([A-Za-z]{3,})(?=\d)',lambda m:m[0] if m[0]=='PbI' else m[0]+' ',value)
    value=re.sub(r'%(?=[A-Za-z])','% ',value)
    return value.replace('Se006','Se 006').replace('Se00L','Se 00L').replace('axial00L','axial 00L').replace('projectedQz','projected Qz').replace('nominalL','nominal L')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',required=True,type=Path)
    ap.add_argument('--metadata',required=True,type=Path)
    ap.add_argument('--release',default='2026-09-10_v9')
    args=ap.parse_args(); project=args.project.resolve(); release=LIB/'releases'/args.release
    curated=read(args.metadata); imported=read(release/'provenance/import_manifest.json')
    source=read(release/'provenance/source_snapshot.json')
    byorigin={}; byhash={}
    for x in imported['imports']:
        byorigin[pathkey(x['original_path'])]=x['path'];byhash.setdefault(x['sha256'],x['path'])
    for x in source['source_files']:
        byorigin[pathkey(x['original_path'])]=(release/x['archived_path']).relative_to(LIB).as_posix()
    for x in imported['embedded_media']: byhash.setdefault(x['sha256'],x['path'])
    missing=[]
    def resolve(name, copy_asset=False):
        if isinstance(name,dict): name=name.get('path') or name.get('file')
        if not name:return None
        if str(name).startswith('ppt/media/'):
            matches=[x['path'] for x in imported['embedded_media'] if x['part']==name]
            return matches[0] if matches else None
        p=Path(name);p=p if p.is_absolute() else project/p
        found=byorigin.get(pathkey(p))
        if found and (LIB/found).is_file(): return found
        if copy_asset and p.is_file():
            hashed=digest(p)
            if hashed in byhash: return byhash[hashed]
            dest=release/'assets/additional'/p.name
            if dest.exists() and digest(dest)!=hashed:dest=dest.with_name(dest.stem+'_'+hashed[:8]+dest.suffix)
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
            out=dest.relative_to(LIB).as_posix();byorigin[pathkey(p)]=out;byhash[hashed]=out
            return out
        missing.append(str(name));return None
    def entry(path,label=None):
        return {'path':path,'format':Path(path).suffix[1:].upper(),'label':label or Path(path).name}
    slides=imported['slides'];assets=[]
    for family in curated['families']:
        kind=family['type']; kind={'static':'figure','movie':'animation'}.get(kind,kind)
        deckuses=family.get('deck_uses',[])
        numbers=sorted(set(x['slide'] for x in deckuses)|set(family.get('slides',[])))
        exports=[(p,resolve(p,True)) for p in family.get('preferred_files',[])]
        exports=[(p,r) for p,r in exports if r]
        variants=[entry(r,Path(str(p)).name) for p,r in exports]
        for name in family.get('alternate_files',[]):
            r=resolve(name,True)
            if r: variants.append(entry(r))
        deckmedia=[]
        for use in deckuses:
            records=use.get('media',[])
            if use.get('media_part'):records=records+[{'part':use['media_part']}]
            for record in records:
                r=resolve(record['part'])
                if r and r.endswith('.mp4') and r not in deckmedia:deckmedia.append(r)
                elif r:variants.append(entry(r,'Exact embedded image: '+Path(r).name))
        preferred=None
        if kind=='animation' and deckmedia:
            preferred=entry(deckmedia[0], 'Exact movie embedded in v9')
            variants.extend(entry(p,'Other exact movie embedded in v9') for p in deckmedia[1:])
        elif exports: preferred=entry(exports[0][1])
        elif numbers:
            preferred=entry(slides[numbers[0]-1]['preview'],'Exact rendered slide')
        if not preferred: raise RuntimeError('No archived preferred view: '+family['id'])
        if numbers and kind=='figure':preferred['preview']=slides[numbers[0]-1]['preview']
        if preferred['format']=='MP4':
            # Prefer a matching export still; for embedded clips use the exact poster relationship.
            match=[x for x in imported['embedded_media'] if x['path']==preferred['path']]
            if match:
                slide=slides[match[0]['slides'][0]-1]
                posters=[p for p in slide['media_paths'] if Path(p).suffix.lower() in ['.png','.jpg','.jpeg']]
                if posters: preferred['preview']=posters[0]
            if 'preview' not in preferred:
                paths=[Path(preferred['path']).with_name(Path(preferred['path']).stem+'_still.png').as_posix()]
                paths += [r for p,r in exports if str(p).endswith('.png')]
                found=next((p for p in paths if (LIB/p).is_file()),None)
                if found:preferred['preview']=found
            ffprobe=Path('C:/ffmpeg/bin/ffprobe.exe')
            if ffprobe.is_file():
                result=subprocess.run([str(ffprobe),'-v','error','-show_entries','format=duration','-of','json',str(LIB/preferred['path'])],capture_output=True,text=True,check=True)
                preferred['duration_seconds']=float(json.loads(result.stdout)['format']['duration'])
        sources=[]
        for name in family.get('source_generators',[])+family.get('provenance_files',[])+family.get('data_files',[]):
            r=resolve(name)
            if r:sources.append(entry(r))
        for number in numbers:
            for chart in slides[number-1]['chart_parts']:
                r=(release/'data/native_chart_packages'/chart).relative_to(LIB).as_posix()
                if (LIB/r).exists():sources.append(entry(r,'Original editable chart XML'))
            if slides[number-1]['chart_parts']:
                sources.append(entry((release/'data/native_chart_index.json').relative_to(LIB).as_posix(),'Chart-to-workbook and CSV index'))
        if family['id'].startswith('pbi2-stack-'):
            sources.append(entry((release/'assets/figures/pbi2_matrix_to_stack_captions.md').relative_to(LIB).as_posix(),'Stacking-figure captions'))
        if family['id'] in ['bi2se3-profiles','bi2te3-profiles']:
            sources.append(entry((release/'source/rebuild/replot_profiles.py').relative_to(LIB).as_posix(),'Portable profile replot adapter'))
            sources.append(entry((release/'source/README.md').relative_to(LIB).as_posix(),'Replot instructions and scientific provenance'))
            material='se' if family['id']=='bi2se3-profiles' else 'te'
            sources.append(entry((release/f'source/rebuild/requirements-{material}.txt').relative_to(LIB).as_posix(),'Pinned plotting dependencies'))
            for p in sorted((release/f'source/direct_data/{material}_profiles').glob('*')):
                if p.suffix in ['.csv','.json','.npz']:
                    sources.append(entry(p.relative_to(LIB).as_posix()))
        seen={preferred['path']};distinct=[]
        for v in variants:
            if v['path'] not in seen:distinct.append(v);seen.add(v['path'])
        asset={'id':family['id'],'title':prose(family['title']),'kind':kind,'description':prose(family['what_it_shows']),
            'usage':prose(family['recommended_use']),'limitations':prose(family.get('limitations',[])),
            'status':prose(family.get('scientific_status','')),'slide_uses':numbers,'preferred':preferred,'variants':distinct,
            'sources':list({s['path']:s for s in sources}.values()),
            'opening_state':family.get('opening_state'),'ending_state':family.get('ending_state'),
            'related_asset_ids':family.get('related_families',[])}
        assets.append(asset)
        for number in numbers:slides[number-1]['asset_ids'].append(asset['id'])
    explorer=release/'assets/interactive/surface-population-explorer.html'
    if explorer.is_file():
        assets.append({'id':'surface-population-explorer','title':'Surface-population explorer','kind':'interactive',
            'description':'Archived interactive companion for exploring surface-termination populations.',
            'usage':'Optional historical exploration, retained separately from the current slide selections.',
            'limitations':['This companion contains earlier conditional trials. It is not an accepted joint refit and is not linked from the current v9 PPT.'],
            'status':'Historical interactive companion','slide_uses':[],
            'preferred':entry(explorer.relative_to(LIB).as_posix()),'variants':[],'sources':[],
            'opening_state':None,'ending_state':None,'related_asset_ids':['bi2se3-termination','bi2te3-termination']})
    # Preserve every exact extracted media part as a discoverable download from its slide.
    for slide in slides:
        slide['media_files']=[entry(p) for p in slide['media_paths']]
    assets.sort(key=lambda a:(min(a['slide_uses']) if a['slide_uses'] else 999,a['kind'],a['title']))
    catalog={'schema_version':1,'release_id':args.release,'title':'Oriented-powder presentation library',
        'description':'The exact edited v9 presentation, its figures and animations, and the source material preserved for reuse.',
        'presentation':imported['presentation'],'slides':slides,'assets':assets,
        'documentation_path':'README.md','checksums_path':'SHA256SUMS.txt',
        'notices':[{'title':'Preserved label discrepancy on slide 7',
            'text':'The slide says 50% Lorentzian. Its embedded r = 0, 1, 3 incidence animation uses 25%, verified against the matching source manifest and media hash. The archived PPT is unchanged.'}],
        'source_manifest':(release/'provenance/source_snapshot.json').relative_to(LIB).as_posix(),
        'file_inventory_path':'FILES.json'}
    write(LIB/'catalog.json',catalog)
    guide=['# Asset guide', '', 'This guide describes the archived exports; the gallery provides playable previews. Current-deck status is a presentation selection, not certification of a fit.', '']
    for a in assets:
        guide += ['## '+a['title'], '', a['description'], '', 'Use: '+a['usage'], '', 'PPT slides: '+(', '.join(map(str,a['slide_uses'])) or 'Optional library asset')+'.', '',
            'Status: '+a['status'], '', '[Preferred export]('+a['preferred']['path'].replace(' ','%20')+')', '']
        if a['opening_state']:guide += ['Opening: '+a['opening_state'], '']
        if a['ending_state']:guide += ['Ending: '+a['ending_state'], '']
        guide += ['- '+v for v in a['limitations']]+['']
    (LIB/'ASSET_GUIDE.md').write_text('\n'.join(guide),encoding='utf-8')
    write(release/'provenance/curated_metadata.json',curated)
    write(release/'provenance/catalog_resolution.json',{'missing_references':sorted(set(missing)),'asset_count':len(assets),'exact_movie_count':sum(x['path'].endswith('.mp4') for x in imported['embedded_media'])})
    print(json.dumps({'families':len(assets),'in_ppt':sum(bool(a['slide_uses']) for a in assets),'missing_references':sorted(set(missing))},indent=2))
if __name__=='__main__':main()
