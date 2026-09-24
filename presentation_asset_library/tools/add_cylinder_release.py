"""Archive v10 and its cylinder bridge without rewriting the immutable v9 release.

Run with the verified final PPT and 26 numbered previews. This one-time release
adapter keeps inherited source/media paths in v9 and records the new slide order.
It does not author or render slides. Existing differing release files are refused.
"""
from pathlib import Path
import argparse, copy, hashlib, io, json, re, zipfile
from xml.etree import ElementTree as ET
from assemble_release import NS, relationships, target, store, jsonbytes
from verify_library import digest, verify
from build_gallery import build

LIB = Path(__file__).resolve().parents[1]
RELEASE = LIB / 'releases/2026-09-11_v10'
OLD = LIB / 'releases/2026-09-10_v9'
MOVIE_SHA = '4ba9e53e3bcf6a4dc351a82ce1d22d3c3adc30269b1c4e6bd0d51a58602dd5d1'
PACKAGE_SHA = '4c20081009b51f2b5f1495ac324772da6deab15f92da02bbf786e58664992bc3'

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(jsonbytes(obj))
def entry(path, label=None):
    return {'path':str(path), 'format':Path(path).suffix[1:].upper(), 'label':label or Path(path).name}
def rel(path): return path.relative_to(LIB).as_posix()

def update_readme(deckpath, deck_sha, insert):
    text=(RELEASE/'source/previous_library_state/README.md').read_text(encoding='utf-8')
    intro=(f'The current archived presentation is **[Oriented_Powder_8min_Animated_v10.pptx]({deckpath})**. '
        f'It adds the latest 26-second cylinder-bridge animation as slide {insert}, after the Bi₂Se₃/Bi₂Te₃ comparisons and before PbI₂. '
        'The author-edited v9 slides are retained. The deck has 26 visible slides, no hidden slides, eight embedded movies, '
        'eight editable chart/workbook pairs, and one native parameter table. The historical filename is retained; '
        'this expanded deck has not been retimed to eight minutes. Live PowerPoint playback has not been verified.\n\n'
        f'Deck SHA-256: `{deck_sha}`.\n\n'
        'The exact preceding [v9 presentation](releases/2026-09-10_v9/presentation/Oriented_Powder_8min_Animated_v9.pptx) and its complete release remain preserved.\n\n')
    start=text.index('The current archived presentation');end=text.index('## Find and reuse an asset')
    text=text[:start]+intro+text[end:]
    text=text.replace('speaker notes for all 25 slides','speaker notes for all 26 slides')
    table='| `releases/2026-09-10_v9/presentation/` | Exact final v9 PPT. |'
    additions=(
        '| `releases/2026-09-11_v10/presentation/` | Exact current v10 PPT. |\n'
        '| `releases/2026-09-11_v10/slides/` | All 26 slide previews and UTF-8 speaker notes in current order. |\n'
        '| `releases/2026-09-11_v10/assets/cylinder_bridge_v3/` | Complete sealed cylinder animation, poster, static PDF/SVG/PNG, storyboard, caption, direct arrays, portable generators, fonts and verification receipts. |\n'
        '| `releases/2026-09-11_v10/assets/Cylinder_Bridge_v3.zip` | Original checked standalone cylinder source package for convenient reuse. |\n'
        '| `releases/2026-09-11_v10/data/` | Updated native-chart slide index, referring to unchanged v9 chart/workbook packages. |\n'
        '| `releases/2026-09-11_v10/source/` and `provenance/` | Addition source, preceding catalog snapshot, import mapping, preservation and deck-validation receipts. |\n')
    text=text.replace(table,additions+table)
    heading='## Scientific meaning and one inherited label discrepancy'
    section=('## Cylinder bridge: what the new animation teaches\n\n'
        f'[Play the asset](releases/2026-09-11_v10/assets/cylinder_bridge_v3/index.html), or find it on slide {insert}. '
        'The smooth opening broadens a nearly delta-like 512-layer profile to the eight-layer example. Random in-plane azimuth forms a cylinder from the off-axis rod; rigid mosaic tilts change its orientations; the Ewald sphere selects elastic-scattering loci. '
        'This supplies the finite-thickness framework before the following stacking-disorder examples.\n\n'
        'The teaching curves mix incoherent populations of neighboring integer layer counts and are peak normalized. Their areas are not conserved, and no physical layer-removal rate is claimed. '
        'The later stage uses an illustrative two-Gaussian orientation law. Its weighted loci are not detector-count predictions. '
        'The [full caption](releases/2026-09-11_v10/assets/cylinder_bridge_v3/caption.txt) states the source geometry, coordinate distinction, normalization and omitted intensity/acceptance factors. '
        'The static companion is preserved from v2 and includes ideal-delta reference arrows, while the v3 movie begins with narrow finite peaks.\n\n')
    text=text.replace(heading,section+heading)
    text=text.replace('This archive preserves the deck exactly and records the issue for a future edited release.','The v10 addition preserves this inherited slide and records the issue for a future content revision.')
    text=text.replace('Verified in this release: a complete 252-frame rotation rebuild','Verified in the inherited v9 release: a complete 252-frame rotation rebuild')
    anchor='Replotting stored results is different from refitting'
    rebuild=('For the new cylinder asset, copy `releases/2026-09-11_v10/assets/cylinder_bridge_v3/` to a new working folder first. '
        'Install its pinned requirements and run the following from that copy with FFmpeg/libx264 on PATH:\n\n'
        '```text\npython source/cylinder_bridge.py\npython source/animate_bridge.py --proofs --movie\npython source/build_gallery.py\npython source/verify_science.py\n```\n\n'
        'The default movie build regenerates the opening and decodes the unchanged tail from its bundled, hash-verified v2 movie. '
        'Use `--full-render` to regenerate every frame from local geometry. Original project files and network services are unnecessary. '
        'The sealed v3 package includes direct science, encoding, browser and isolated-portability checks; its 45 listed file hashes are verified again on import.\n\n')
    text=text.replace(anchor,rebuild+anchor)
    text=text.replace('Treat `releases/2026-09-10_v9/` as immutable.','Treat both `releases/2026-09-10_v9/` and `releases/2026-09-11_v10/` as immutable.')
    text=text.replace('Its copy inside this release is historical context','Its copy inside the v9 source snapshot is historical context')
    (LIB/'README.md').write_text(text,encoding='utf-8',newline='\n')

def stage(asset_zip):
    """Unpack the sealed source package without caches or unlisted loose files."""
    assert digest(asset_zip)==PACKAGE_SHA, 'Unexpected cylinder source package'
    archive_path=store(RELEASE/'assets/Cylinder_Bridge_v3.zip',asset_zip.read_bytes())
    destination=RELEASE/'assets/cylinder_bridge_v3'
    with zipfile.ZipFile(asset_zip) as z:
        assert z.testzip() is None
        for member in z.infolist():
            p=Path(member.filename)
            assert not p.is_absolute() and '..' not in p.parts
            assert p.parts[0]=='cylinder_bridge_v3'
            if not member.is_dir(): store(destination/Path(*p.parts[1:]),z.read(member))
    result=verify(destination)
    assert result['ok'], result
    assert digest(destination/'Cylinder_Bridge.mp4')==MOVIE_SHA
    return destination, archive_path, result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--deck',required=True,type=Path)
    ap.add_argument('--renders',required=True,type=Path)
    ap.add_argument('--asset-zip',required=True,type=Path)
    ap.add_argument('--slide-number',default=19,type=int)
    ap.add_argument('--validation',action='append',type=Path,default=[])
    ap.add_argument('--authoring-source',action='append',type=Path,default=[])
    args=ap.parse_args(); insert=args.slide_number
    baseline=RELEASE/'source/previous_catalog.json'
    if not baseline.exists():
        assert read(LIB/'catalog.json')['release_id']=='2026-09-10_v9'
        store(baseline,(LIB/'catalog.json').read_bytes())
        for name in ['README.md','ASSET_GUIDE.md','FILES.json','SHA256SUMS.txt','index.html']:
            store(RELEASE/'source/previous_library_state'/name,(LIB/name).read_bytes())
    old=read(baseline); assert old['presentation']['slide_count']==25
    prior_files=read(RELEASE/'source/previous_library_state/FILES.json')['files']
    preserved=[x for x in prior_files if x['path'].startswith('releases/2026-09-10_v9/')]
    assert all(digest(LIB/x['path'])==x['sha256'] for x in preserved), 'An immutable v9 file differs'
    assetdir,archive_path,source_verify=stage(args.asset_zip)
    raw=args.deck.read_bytes(); deckpath=store(RELEASE/'presentation'/args.deck.name,raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z: pkg={n:z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(LIB/old['presentation']['path']) as z: oldpkg={n:z.read(n) for n in z.namelist()}
    allowed_insertion_parts={'[Content_Types].xml','ppt/presentation.xml','ppt/_rels/presentation.xml.rels','docProps/app.xml','docProps/core.xml'}
    inherited_parts=[p for p in oldpkg if p not in allowed_insertion_parts]
    assert all(pkg.get(p)==oldpkg[p] for p in inherited_parts), 'An inherited package dependency changed'
    px=ET.fromstring(pkg['ppt/presentation.xml']); pr=relationships(pkg,'ppt/presentation.xml')
    order=[target('ppt/presentation.xml',pr[s.get('{'+NS['r']+'}id')].get('Target')) for s in px.find('p:sldIdLst',NS)]
    assert len(order)==26 and 1<=insert<=26
    old_by_part={s['part']:s for s in old['slides']}
    assert [p for i,p in enumerate(order,1) if i!=insert]==[s['part'] for s in old['slides']]
    media_by_sha={x['sha256']:x['path'] for x in read(OLD/'provenance/import_manifest.json')['embedded_media']}
    # Match every portable source export, including the bridge poster, by its bytes.
    for p in assetdir.rglob('*'):
        if p.is_file(): media_by_sha.setdefault(digest(p),rel(p))
    slides=[]; media={}; unchanged=[]
    for number,part in enumerate(order,1):
        xml=ET.fromstring(pkg[part]); assert xml.get('show')!='0'
        inherited=old_by_part.get(part)
        if inherited:
            assert pkg[part]==oldpkg[part], f'Inherited slide content changed: {part}'
            unchanged.append({'old_slide':inherited['number'],'new_slide':number,'part':part,'sha256':hashlib.sha256(pkg[part]).hexdigest()})
        texts=[''.join(t.text or '' for t in p.findall('.//a:t',NS)) for p in xml.findall('.//a:p',NS)]
        texts=[t for t in texts if t.strip()]; notes=''; members=[]; charts=[]
        for r in relationships(pkg,part).values():
            if r.get('TargetMode')=='External': continue
            path=target(part,r.get('Target'))
            if path.startswith('ppt/media/'):
                sha=hashlib.sha256(pkg[path]).hexdigest()
                out=media_by_sha.get(sha) or store(RELEASE/'assets/deck_embedded'/Path(path).name,pkg[path])
                m=media.setdefault(path,{'part':path,'path':out,'sha256':sha,'bytes':len(pkg[path]),'slides':[]})
                if number not in m['slides']:m['slides'].append(number)
                if out not in members: members.append(out)
            elif r.get('Type','').endswith('/notesSlide'):
                n=ET.fromstring(pkg[path]); body=[]
                for sp in n.findall('.//p:sp',NS):
                    ph=sp.find('p:nvSpPr/p:nvPr/p:ph',NS)
                    if ph is not None and ph.get('type')=='body':
                        body += [''.join(t.text or '' for t in p.findall('.//a:t',NS)) for p in sp.findall('.//a:p',NS)]
                notes='\n'.join(body)
            elif r.get('Type','').endswith('/chart'):
                assert pkg[path]==oldpkg[path], 'Native chart changed'
                charts.append(path)
        preview=store(RELEASE/'slides'/f'slide-{number:02d}.png',(args.renders/f'slide-{number:02d}.png').read_bytes())
        notespath=store(RELEASE/'slides'/f'slide-{number:02d}-notes.txt',(notes+'\n').encode('utf-8'))
        saved_name=xml.find('p:cSld',NS).get('name')
        slides.append({'number':number,'title':texts[0] if texts else (saved_name or f'Slide {number}'),'texts':texts,'hidden':False,'part':part,
            'preview':preview,'notes_path':notespath,'media_paths':members,'chart_parts':charts,
            'table_paths':inherited['table_paths'] if inherited else [],'asset_ids':copy.deepcopy(inherited['asset_ids']) if inherited else ['cylinder-bridge'],
            'media_files':[entry(p) for p in members]})
    # The prior native chart/workbook packages are retained exactly, with a new slide index.
    native_parts=[p for p in oldpkg if p.startswith(('ppt/charts/','ppt/embeddings/'))]
    assert all(pkg.get(p)==oldpkg[p] for p in native_parts)
    chart_index=read(OLD/'data/native_chart_index.json')
    for c in chart_index: c['slides']=[n+(n>=insert) for n in c['slides']]
    write(RELEASE/'data/native_chart_index.json',chart_index)
    movies=[m for m in media.values() if m['path'].endswith('.mp4')]
    assert len(movies)==8 and any(m['sha256']==MOVIE_SHA and m['slides']==[insert] for m in movies)
    assets=copy.deepcopy(old['assets'])
    for a in assets:
        a['slide_uses']=[n+(n>=insert) for n in a['slide_uses']]
        if a['id']=='pbi2-matrices':a['usage']=a['usage'].replace('slide 23','slide 24')
        if a['preferred'].get('label')=='Exact movie embedded in v9':
            a['preferred']['label']='Exact movie retained from v9 in v10'
        for s in a['sources']:
            if s['path']==rel(OLD/'data/native_chart_index.json'):
                s['path']=rel(RELEASE/'data/native_chart_index.json')
        # Only presentation previews change; scientific exports keep their original release path.
        for key in ['path','preview']:
            p=a['preferred'].get(key,''); match=re.fullmatch(r'releases/2026-09-10_v9/slides/slide-(\d+)\.png',p)
            if match:
                n=int(match[1]);a['preferred'][key]=rel(RELEASE/'slides'/f'slide-{n+(n>=insert):02d}.png')
    def ae(name,label=None):return entry(rel(assetdir/name),label)
    cylinder={
        'id':'cylinder-bridge','title':'Finite thickness: rods, cylinders and Ewald selection','kind':'animation',
        'description':'Narrow finite-stack peaks broaden smoothly to the eight-layer example. Random in-plane azimuth distributes the rod around a cylinder, rigid mosaic tilts spread its orientations, and the Ewald sphere selects the allowed loci.',
        'usage':f'Bridge after the Bi₂Se₃/Bi₂Te₃ results and before PbI₂, on slide {insert}. The static PDF/SVG/PNG provides the dissertation or manual companion.',
        'limitations':[
            'Teaching geometry and peak-normalized profiles, not material-specific fitted intensities or an allowed-reflection list. Finite thickness already produces fringes; stacking faults would redistribute intensity on the existing rods.',
            'The smooth opening mixes incoherent populations of neighboring integer layer counts from mean N=512 to N=8. It does not use fractional atomic layers or preserve the plotted integrated area. Visible broadening accelerates; no physical layer-removal rate is claimed.',
            'Mosaicity is a rigid rotation about the reciprocal origin, preserving |Q| and intrinsic L. Intrinsic L is not laboratory Qz after tilt. The two Gaussian teaching components are distinct from fitted BiX mosaic parameters.',
            'Selected loci obey the exact elastic Ewald condition. Brightness is qualitative: structure factors, coarea/detector Jacobians, optics, beam spread and opaque-substrate acceptance are omitted. Qz is a coordinate axis; no specular r=0 response is added.',
            'The static companion is byte-preserved from v2 and retains its ideal-delta reference. The v3 movie opens with narrow finite N=512 peaks. Its final 8–26 seconds use the hash-verified retained v2 tail; full geometry rendering remains available.'
        ],
        'status':'Verified generic finite-stack geometry and qualitative weighted selection; not a fitted detector-count result.',
        'slide_uses':[insert],
        'preferred':{**ae('Cylinder_Bridge.mp4','Exact v3 movie embedded in v10'),'preview':rel(assetdir/'storyboard/frame_00.0s.png'),'duration_seconds':26.0},
        'variants':[ae('Cylinder_Bridge.pdf','Static four-panel PDF'),ae('Cylinder_Bridge.svg','Editable vector SVG'),ae('Cylinder_Bridge.png','High-resolution static PNG'),ae('Cylinder_Bridge_poster.png','Animation poster'),ae('index.html','Complete offline asset preview')],
        'sources':[entry(archive_path,'Complete sealed v3 source package'),ae('README.md','Rebuild and reuse instructions'),ae('caption.txt','Full static and animation caption'),ae('requirements.txt','Pinned dependencies'),ae('source/cylinder_bridge.py','Static geometry and direct arrays'),ae('source/animate_bridge.py','Animation generator with full-render option'),ae('data/model_arrays.npz','Exact model arrays'),ae('data/opening_profiles.npz','Dense smooth-opening profiles'),ae('data/opening_normalization.csv','Opening normalization'),ae('data/rod_profile.csv','Direct rod profile'),ae('data/orientation_quadrature.csv','Orientation weights'),ae('provenance/animation.json','Movie version, timeline and hash'),ae('provenance/Cylinder_Bridge.json','Scientific model and provenance'),ae('provenance/science_review.json','Independent science verification'),ae('provenance/visual_portability_review.json','Rendering and portability verification'),ae('SHA256SUMS.txt','Complete v3 checksums')],
        'opening_state':'Nearly delta-like finite peaks from a 512-layer stack.',
        'ending_state':'Orientation-weighted tilted-cylinder loci on the Ewald sphere.',
        'related_asset_ids':['ewald-mosaic','ewald-detector','pbi2-matrices'],
        'source_thread':'codex://threads/01a08bed-6ea7-7721-934d-f260c5ed4faf','asset_version':'cylinder_bridge_v3'}
    assets.append(cylinder);assets.sort(key=lambda a:(min(a['slide_uses']) if a['slide_uses'] else 999,a['kind'],a['title']))
    catalog=copy.deepcopy(old)
    catalog.update({'release_id':'2026-09-11_v10','description':'The edited v10 deck adds the latest cylinder bridge animation to the exact retained v9 slides, with portable figures, sources and provenance.','presentation':{'path':deckpath,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'slide_count':26,'embedded_movies':8,'native_charts':8,'native_tables':1},'slides':slides,'assets':assets,
        'source_manifest':rel(RELEASE/'provenance/source_snapshot.json')})
    catalog['notices'][0]['text']='The retained slide says 50% Lorentzian. Its embedded r = 0, 1, 3 incidence animation uses 25%, verified against the matching source manifest and media hash. This inherited label is unchanged by the cylinder-bridge addition.'
    records=[]
    for p in args.validation:
        records.append(store(RELEASE/'provenance/deck_validation'/p.name,p.read_bytes()))
    for p in args.authoring_source:
        store(RELEASE/'source/deck_authoring'/p.name,p.read_bytes())
    write(RELEASE/'provenance/source_snapshot.json',{'schema_version':1,'release_id':'2026-09-11_v10','source_thread':cylinder['source_thread'],
        'inherited_source_manifest':rel(OLD/'provenance/source_snapshot.json'),'inherited_release_immutable':True,
        'cylinder_source_root':rel(assetdir),'cylinder_package':archive_path,'cylinder_package_sha256':PACKAGE_SHA,'cylinder_source_verification':source_verify,
        'note':'The complete sealed cylinder v3 package is preserved. Existing scientific sources remain in immutable v9. This release adds one slide and performs no scientific refit.'})
    write(RELEASE/'provenance/import_manifest.json',{'schema_version':1,'release_id':'2026-09-11_v10','presentation':catalog['presentation'],'slides':slides,'embedded_media':list(media.values()),'deck_validation':records})
    write(RELEASE/'provenance/preservation_review.json',{'ok':True,'unchanged_v9_files':len(preserved),'unchanged_slide_xml':unchanged,'unchanged_inherited_ppt_parts':len(inherited_parts),'permitted_insertion_package_parts':sorted(allowed_insertion_parts),'unchanged_native_parts':len(native_parts),'new_movie_sha256':MOVIE_SHA,'source_package_check':source_verify,'slide_insertion':insert,'inherited_slide_7_label_discrepancy_preserved':True})
    write(LIB/'catalog.json',catalog)
    guide=['# Asset guide','','This guide describes the archived exports; the gallery provides playable previews. Current-deck status is a presentation selection, not certification of a fit.','']
    for a in assets:
        guide += ['## '+a['title'],'',a['description'],'','Use: '+a['usage'],'','PPT slides: '+(', '.join(map(str,a['slide_uses'])) or 'Optional library asset')+'.','','Status: '+a['status'],'','[Preferred export]('+a['preferred']['path'].replace(' ','%20')+')','']
        if a.get('opening_state'):guide += ['Opening: '+a['opening_state'],'']
        if a.get('ending_state'):guide += ['Ending: '+a['ending_state'],'']
        guide += ['- '+s for s in a['limitations']]+['']
    (LIB/'ASSET_GUIDE.md').write_text('\n'.join(guide),encoding='utf-8')
    (LIB/'index.html').write_text(build(catalog),encoding='utf-8',newline='\n')
    update_readme(deckpath,catalog['presentation']['sha256'],insert)
    print(json.dumps({'release':str(RELEASE),'deck_sha256':catalog['presentation']['sha256'],'assets':len(assets),'animations':sum(a['kind']=='animation' for a in assets),'slides':26,'movies':len(movies),'preserved_v9_files':len(preserved)},indent=2))

if __name__=='__main__':main()
