"""Independent read-only preservation and relationship audit of v10."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import hashlib
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'presentation_asset_library/releases/2026-09-10_v9/presentation/Oriented_Powder_8min_Animated_v9.pptx'
TARGET = ROOT / 'output/presentations/Oriented_Powder_8min_Animated_v10.pptx'
if len(sys.argv) > 1:
    TARGET = Path(sys.argv[1]).resolve()
MOVIE = ROOT / 'output/cylinder_bridge_v3/Cylinder_Bridge.mp4'
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships',
      'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def resolve(part, target):
    if target.startswith('/'):
        return target.lstrip('/')
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))

def relationship_part(part):
    p = PurePosixPath(part)
    return str(p.parent / '_rels' / (p.name + '.rels'))

def relationships(z, part):
    name = relationship_part(part)
    return {e.attrib['Id']: e.attrib for e in ET.fromstring(z.read(name))} if name in z.namelist() else {}

def slide_parts(z):
    root = ET.fromstring(z.read('ppt/presentation.xml'))
    rels = relationships(z, 'ppt/presentation.xml')
    return [resolve('ppt/presentation.xml', rels[s.attrib['{' + NS['r'] + '}id']]['Target'])
            for s in root.findall('p:sldIdLst/p:sldId', NS)]

def main():
    failures = []
    checks = {}
    source_hash = sha(SOURCE.read_bytes())
    checks['source_v9_unchanged'] = source_hash == '0feca65d8e57c764666012cc75cd880da660fd1fea12eedba0cec69193c2cec3'
    with ZipFile(SOURCE) as a, ZipFile(TARGET) as b:
        an, bn = set(a.namelist()), set(b.namelist())
        old, new = slide_parts(a), slide_parts(b)
        checks['slide_counts_25_to_26'] = len(old) == 25 and len(new) == 26
        checks['old_slide_order_preserved'] = old == new[:18] + new[19:]
        checks['no_hidden_slides'] = all(ET.fromstring(b.read(p)).get('show', '1') not in ('0', 'false') for p in new)
        removed = sorted(an - bn)
        changed = sorted(n for n in an & bn if a.read(n) != b.read(n))
        allowed = {'[Content_Types].xml', 'ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels', 'docProps/app.xml', 'docProps/core.xml'}
        checks['no_existing_parts_removed'] = not removed
        checks['only_package_metadata_changed'] = not set(changed) - allowed
        checks['all_old_slide_xml_unchanged'] = all(a.read(n) == b.read(n) for n in old)
        checks['all_old_slide_relationships_unchanged'] = all(a.read(relationship_part(n)) == b.read(relationship_part(n)) for n in old)
        preserved_prefixes = ['ppt/notesSlides/', 'ppt/charts/', 'ppt/embeddings/', 'ppt/media/']
        preserved = {p: all(a.read(n) == b.read(n) for n in an if n.startswith(p)) for p in preserved_prefixes}
        checks['old_notes_charts_workbooks_media_unchanged'] = all(preserved.values())
        movie_parts = sorted(n for n in bn if n.startswith('ppt/media/') and n.lower().endswith('.mp4'))
        old_movie_parts = sorted(n for n in an if n.startswith('ppt/media/') and n.lower().endswith('.mp4'))
        checks['movies_7_to_8'] = len(old_movie_parts) == 7 and len(movie_parts) == 8
        chart_parts = sorted(n for n in bn if re.fullmatch(r'ppt/charts/chart\d+\.xml', n))
        workbooks = sorted(n for n in bn if n.startswith('ppt/embeddings/') and n.lower().endswith('.xlsx'))
        tables = sum(len(ET.fromstring(b.read(n)).findall('.//a:tbl', NS)) for n in new)
        checks['eight_native_charts_and_workbooks'] = len(chart_parts) == len(workbooks) == 8
        checks['one_native_table'] = tables == 1

        part = new[18]
        root = ET.fromstring(b.read(part))
        rels = relationships(b, part)
        video_targets = {resolve(part, r['Target']) for r in rels.values() if r['Type'].endswith(('/video', '/media'))}
        checks['new_movie_internal_single_target'] = len(video_targets) == 1 and all(r.get('TargetMode', 'Internal') == 'Internal' for r in rels.values())
        checks['new_movie_exact_v3_hash'] = bool(video_targets) and all(sha(b.read(n)) == sha(MOVIE.read_bytes()) for n in video_targets)
        dimensions = ET.fromstring(b.read('ppt/presentation.xml')).find('p:sldSz', NS).attrib
        pics = root.findall('.//p:pic', NS)
        movie_pic = next((p for p in pics if p.find('.//a:videoFile', NS) is not None), None)
        checks['movie_picture_exists'] = movie_pic is not None
        if movie_pic is not None:
            xfrm = movie_pic.find('p:spPr/a:xfrm', NS)
            off, ext = xfrm.find('a:off', NS).attrib, xfrm.find('a:ext', NS).attrib
            checks['full_slide_movie_placement'] = off == {'x': '0', 'y': '0'} and ext == dimensions
        video = root.find('.//p:video', NS)
        checks['video_timing_present'] = video is not None
        conditions = [e.attrib for e in root.findall('.//p:cond', NS)]
        time_nodes = [e.attrib for e in root.findall('.//p:cTn', NS)]
        play_calls = [c.attrib for c in root.findall('.//p:cmd', NS) if c.get('cmd') == 'playFrom(0.0)']
        checks['click_trigger_present'] = (any(c.get('evt') == 'onClick' for c in conditions)
            or (any(t.get('nodeType') == 'clickEffect' and t.get('presetClass') == 'mediacall' for t in time_nodes)
                and bool(play_calls) and any(c.get('delay') == 'indefinite' for c in conditions)
                and any(c.get('evt') == 'onNext' for c in conditions)))
        checks['media_last_frame_hold'] = video is not None and video.find('p:cMediaNode/p:cTn', NS) is not None and video.find('p:cMediaNode/p:cTn', NS).get('fill') == 'hold'
        checks['no_new_slide_auto_advance'] = root.find('p:transition', NS) is None or root.find('p:transition', NS).get('advTm') is None

        broken, external = [], []
        for n in sorted(bn):
            if not n.endswith('.rels'):
                continue
            pp = PurePosixPath(n)
            owner = '' if n == '_rels/.rels' else str(pp.parent.parent / pp.name[:-5])
            for r in ET.fromstring(b.read(n)):
                if r.get('TargetMode') == 'External':
                    external.append({'part': n, **r.attrib})
                else:
                    resolved = resolve(owner, r.get('Target', '')).split('#')[0]
                    if resolved not in bn:
                        broken.append({'part': n, 'target': resolved})
        checks['all_internal_relationship_targets_exist'] = not broken
        new_parts = sorted(bn - an)
        checks['no_new_external_relationships'] = not any(r['part'] in new_parts for r in external)
        for key, value in checks.items():
            if not value:
                failures.append(key)
        receipt = dict(status='pass' if not failures else 'fail', checks=checks, failures=failures,
            source_sha256=source_hash, candidate_sha256=sha(TARGET.read_bytes()), source=str(SOURCE), candidate=str(TARGET),
            new_slide_number=19, new_slide_part=part, old_slide_part_order=old, new_slide_part_order=new,
            changed_existing_parts=changed, removed_parts=removed, added_parts=new_parts, preserved_families=preserved,
            movie_source_sha256=sha(MOVIE.read_bytes()), new_movie_targets=sorted(video_targets),
            movie_count=len(movie_parts), native_chart_count=len(chart_parts), embedded_workbook_count=len(workbooks),
            native_table_count=tables, new_slide_timing_conditions=conditions, new_slide_time_nodes=time_nodes,
            broken_relationships=broken, existing_external_relationships=external,
            limitation='OpenXML and render checks do not constitute PowerPoint playback testing.')
        (HERE / 'independent_package_audit.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        print(json.dumps({'status': receipt['status'], 'failures': failures, 'changed_parts': changed, 'added_parts': new_parts}, indent=2))
    return bool(failures)

if __name__ == '__main__':
    sys.exit(main())
