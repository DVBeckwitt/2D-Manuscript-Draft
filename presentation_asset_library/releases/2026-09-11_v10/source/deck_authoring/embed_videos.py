"""Embed MP4s in existing poster pictures without re-exporting the deck.

Usage: python embed_videos.py --input draft.pptx --mapping videos.json
           --output candidate.pptx [--report private_report.json]

Mapping is a JSON list of {slide_part, shape_name, video_path}; for example
slide_part='ppt/slides/slide13.xml'. Optional shape_id selects a verified picture
ID when export discarded its name. All mapped slides must be animation-free.
The original image, crop, dimensions, position, and other slide objects stay intact.
This is OOXML packaging only, not a replacement for PowerPoint playback review.

Sources:
https://learn.microsoft.com/en-us/office/open-xml/presentation/how-to-add-a-video-to-a-slide-in-a-presentation
https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.command
https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.commontimenode
https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.commonmedianode
https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/9bdaa76e-c714-4034-8c29-ac42071e3484
https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/b2f15f11-5b40-4f67-ae95-5a510c3bea06
https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/a65b76db-6abc-4989-8cd1-baa9a3500f6f
https://raw.githubusercontent.com/dotnet/Open-XML-SDK/v3.0.1/data/schemas/schemas_openxmlformats_org_drawingml_2006_main.json
https://support.microsoft.com/en-us/powerpoint/insert-and-play-a-video-file-from-your-computer
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import subprocess
import zipfile
from pathlib import Path

from lxml import etree as ET

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
}
VIDEO_REL = NS['r'] + '/video'
MEDIA_REL = 'http://schemas.microsoft.com/office/2007/relationships/media'
MEDIA_EXT = '{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}'
FFPROBE = Path('C:/ffmpeg/bin/ffprobe.exe')


def q(prefix, local):
    return '{' + NS[prefix] + '}' + local


def element(prefix, local, **attributes):
    return ET.Element(q(prefix, local), {k: str(v) for k, v in attributes.items()})


def sub(parent, prefix, local, **attributes):
    child = element(prefix, local, **attributes)
    parent.append(child)
    return child


def serialize(root):
    return ET.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)


def parse(data):
    return ET.fromstring(data, ET.XMLParser(resolve_entities=False, no_network=True))


def rels_part(part):
    folder, name = posixpath.split(part)
    return posixpath.join(folder, '_rels', name + '.rels')


def target_part(owner, target):
    if target.startswith('/'):
        return target.lstrip('/')
    return posixpath.normpath(posixpath.join(posixpath.dirname(owner), target))


def add_relation(root, target, relation_type):
    used = {n.get('Id') for n in root}
    number = 1
    while f'rId{number}' in used:
        number += 1
    rid = f'rId{number}'
    sub(root, 'rel', 'Relationship', Id=rid, Type=relation_type, Target=target)
    return rid


def probe_video(path, ffprobe=FFPROBE):
    result = subprocess.run(
        [str(ffprobe), '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=codec_name,pix_fmt,width,height,avg_frame_rate,duration,nb_frames:format=duration',
         '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if not data.get('streams'):
        raise ValueError(f'No video stream in {path}')
    stream = data['streams'][0]
    duration = float(stream.get('duration') or data['format']['duration'])
    if duration <= 0 or stream.get('codec_name') != 'h264' or stream.get('pix_fmt') != 'yuv420p':
        raise ValueError(f'Expected a positive-duration H264 yuv420p MP4: {path}')
    return dict(stream, duration_seconds=duration, duration_ms=round(duration * 1000))


def start_condition(parent, delay='0'):
    return sub(sub(parent, 'p', 'stCondLst'), 'p', 'cond', delay=delay)


def timing(shape_id, duration_ms):
    """One click-effect command starts a separately addressable media node.

    A normal main sequence consumes the next presenter click. The indefinite
    media start condition prevents playback on slide entry. The media command
    starts that node explicitly. One repeat and a held fill retain the last
    frame while the root timing container remains active until slide advance.
    """
    root = element('p', 'timing')
    tnlist = sub(root, 'p', 'tnLst')
    root_time = sub(sub(tnlist, 'p', 'par'), 'p', 'cTn',
                    id=1, dur='indefinite', restart='never', nodeType='tmRoot')
    root_children = sub(root_time, 'p', 'childTnLst')
    seq = sub(root_children, 'p', 'seq', concurrent=1, nextAc='seek')
    seq_time = sub(seq, 'p', 'cTn', id=2, dur='indefinite', nodeType='mainSeq')
    seq_children = sub(seq_time, 'p', 'childTnLst')
    click_group = sub(sub(seq_children, 'p', 'par'), 'p', 'cTn', id=3, fill='hold')
    start_condition(click_group, 'indefinite')
    inner_group = sub(sub(sub(click_group, 'p', 'childTnLst'), 'p', 'par'),
                      'p', 'cTn', id=4, fill='hold')
    start_condition(inner_group)
    effect = sub(sub(sub(inner_group, 'p', 'childTnLst'), 'p', 'par'), 'p', 'cTn',
                 id=5, presetID=83, presetClass='mediacall', presetSubtype=0,
                 fill='hold', nodeType='clickEffect')
    start_condition(effect)
    cmd = sub(sub(effect, 'p', 'childTnLst'), 'p', 'cmd', type='call', cmd='playFrom(0.0)')
    behavior = sub(cmd, 'p', 'cBhvr')
    sub(behavior, 'p', 'cTn', id=6, dur=1, fill='hold')
    sub(sub(behavior, 'p', 'tgtEl'), 'p', 'spTgt', spid=shape_id)
    for name, event in [('prevCondLst', 'onPrev'), ('nextCondLst', 'onNext')]:
        cond = sub(sub(seq, 'p', name), 'p', 'cond', evt=event, delay=0)
        sub(sub(cond, 'p', 'tgtEl'), 'p', 'sldTgt')
    video = sub(root_children, 'p', 'video', fullScrn=0)
    media = sub(video, 'p', 'cMediaNode', vol=0, mute=1, numSld=1, showWhenStopped=1)
    media_time = sub(media, 'p', 'cTn', id=7, dur=duration_ms, fill='hold',
                     repeatCount=1000, display=0)
    start_condition(media_time, 'indefinite')
    sub(sub(media, 'p', 'tgtEl'), 'p', 'spTgt', spid=shape_id)
    return root


def make_manual_transition(slide):
    transition = slide.find('p:transition', NS)
    if transition is None:
        transition = element('p', 'transition', advClick=1)
        # cSld/clrMapOvr precede transition; timing/extLst follow it.
        following = next((c for c in slide if c.tag in (q('p', 'timing'), q('p', 'extLst'))), None)
        if following is None:
            slide.append(transition)
        else:
            slide.insert(slide.index(following), transition)
    transition.set('advClick', '1')
    transition.attrib.pop('advTm', None)


def embed_one(parts, item, ordinal, ffprobe):
    part = item['slide_part'].lstrip('/')
    video_path = Path(item['video_path']).resolve(strict=True)
    if video_path.suffix.lower() != '.mp4':
        raise ValueError(f'Only MP4 is supported: {video_path}')
    probe = probe_video(video_path, ffprobe)
    slide = parse(parts[part])
    if 'shape_id' in item:
        pictures = [p for p in slide.findall('.//p:pic', NS)
                    if p.find('p:nvPicPr/p:cNvPr', NS).get('id') == str(item['shape_id'])]
    else:
        pictures = [p for p in slide.findall('.//p:pic', NS)
                    if any(p.find('p:nvPicPr/p:cNvPr', NS).get(key) == item['shape_name']
                           for key in ('name', 'descr'))]
    if len(pictures) != 1:
        raise ValueError(f'Expected one poster {item["shape_name"]!r} in {part}, found {len(pictures)}')
    if slide.find('p:timing', NS) is not None:
        raise ValueError(f'{part} already has timing; merge it explicitly before using this helper')
    picture = pictures[0]
    props = picture.find('p:nvPicPr/p:cNvPr', NS)
    props.set('name', item['shape_name'])
    shape_id = props.get('id')
    if props.find('a:hlinkClick', NS) is not None:
        raise ValueError(f'{part} poster already has a click action')
    # Playback belongs to the presenter's main click sequence below. No direct
    # picture hyperlink shortcut is needed: playFrom(0.0) targets the media
    # shape through its shape ID and the root-level video timing node.
    nv_props = picture.find('p:nvPicPr/p:nvPr', NS)
    if nv_props is None:
        nv_props = sub(picture.find('p:nvPicPr', NS), 'p', 'nvPr')
    if nv_props.find('a:videoFile', NS) is not None:
        raise ValueError(f'{part} poster is already a video')
    relation_part = rels_part(part)
    relations = parse(parts[relation_part]) if relation_part in parts else ET.Element(q('rel', 'Relationships'), nsmap={None:NS['rel']})
    video_data = video_path.read_bytes()
    digest = hashlib.sha256(video_data).hexdigest()
    media_part = f'ppt/media/animation_{ordinal:02d}_{digest[:12]}.mp4'
    if media_part in parts and parts[media_part] != video_data:
        raise ValueError(f'Media collision: {media_part}')
    parts[media_part] = video_data
    relative = posixpath.relpath(media_part, posixpath.dirname(part))
    video_rid = add_relation(relations, relative, VIDEO_REL)
    media_rid = add_relation(relations, relative, MEDIA_REL)
    video_file = element('a', 'videoFile')
    video_file.set(q('r', 'link'), video_rid)
    # The media choice precedes custDataLst and extLst in CT_ApplicationNonVisualDrawingProps.
    following = next((c for c in nv_props if c.tag in (q('p', 'custDataLst'), q('p', 'extLst'))), None)
    if following is None:
        nv_props.append(video_file)
    else:
        nv_props.insert(nv_props.index(following), video_file)
    extlist = nv_props.find('p:extLst', NS)
    if extlist is None:
        extlist = sub(nv_props, 'p', 'extLst')
    ext = sub(extlist, 'p', 'ext', uri=MEDIA_EXT)
    media = ET.Element(q('p14', 'media'), nsmap={'p14':NS['p14']})
    media.set(q('r', 'embed'), media_rid)
    ext.append(media)
    make_manual_transition(slide)
    video_timing = timing(shape_id, probe['duration_ms'])
    extlist = slide.find('p:extLst', NS)
    if extlist is None:
        slide.append(video_timing)
    else:
        slide.insert(slide.index(extlist), video_timing)
    parts[part] = serialize(slide)
    parts[relation_part] = serialize(relations)
    return dict(item, slide_part=part, shape_id=shape_id, video_part=media_part,
                bytes=len(video_data), sha256=digest, probe=probe)


def validate(parts, items, expected_total_video_count=None):
    """Check actual resulting XML and bytes, not only authoring inputs."""
    content_types = parse(parts['[Content_Types].xml'])
    assert any(n.get('Extension') == 'mp4' and n.get('ContentType') == 'video/mp4'
               for n in content_types), 'MP4 content type missing'
    for item in items:
        part = item['slide_part']
        slide = parse(parts[part])
        relations = {r.get('Id'):r for r in parse(parts[rels_part(part)])}
        props = slide.xpath('.//p:pic/p:nvPicPr/p:cNvPr[@name=$name]', namespaces=NS, name=item['shape_name'])
        assert len(props) == 1, f'Poster name ambiguous: {part}'
        pic = props[0].getparent().getparent()
        shape_id = props[0].get('id')
        all_ids = [n.get('id') for n in slide.findall('.//p:cNvPr', NS)]
        assert len(all_ids) == len(set(all_ids)), f'Duplicate shape IDs: {part}'
        assert pic.find('p:blipFill/a:blip', NS) is not None, 'Poster removed'
        assert props[0].find('a:hlinkClick', NS) is None
        vf = pic.find('p:nvPicPr/p:nvPr/a:videoFile', NS)
        media = pic.find('.//p14:media', NS)
        assert vf is not None and media is not None
        for rid, expected_type in [(vf.get(q('r','link')), VIDEO_REL), (media.get(q('r','embed')), MEDIA_REL)]:
            rel = relations[rid]
            assert rel.get('Type') == expected_type and rel.get('TargetMode') != 'External'
            target = target_part(part, rel.get('Target'))
            assert target == item['video_part'] and target in parts
            assert hashlib.sha256(parts[target]).hexdigest() == item['sha256']
        times = slide.findall('.//p:timing//p:cTn', NS)
        time_ids = [n.get('id') for n in times]
        assert len(time_ids) == len(set(time_ids)), 'Duplicate time node IDs'
        seq = slide.find('.//p:timing//p:seq', NS)
        assert seq.find('p:cTn', NS).get('nodeType') == 'mainSeq'
        assert seq.find('p:nextCondLst/p:cond', NS).get('evt') == 'onNext'
        assert seq.find('p:cTn/p:childTnLst/p:par/p:cTn/p:stCondLst/p:cond', NS).get('delay') == 'indefinite'
        cmds = slide.findall('.//p:timing//p:cmd', NS)
        assert len(cmds) == 1 and cmds[0].get('cmd') == 'playFrom(0.0)' and cmds[0].get('type') == 'call'
        media_node = slide.find('.//p:timing//p:video/p:cMediaNode', NS)
        assert media_node.get('showWhenStopped') == '1' and media_node.get('numSld') == '1'
        media_time = media_node.find('p:cTn', NS)
        assert media_time.get('fill') == 'hold' and media_time.get('repeatCount') == '1000'
        assert media_time.get('dur') == str(item['probe']['duration_ms'])
        assert media_time.find('p:stCondLst/p:cond', NS).get('delay') == 'indefinite'
        targets = slide.findall('.//p:timing//p:spTgt', NS)
        assert len(targets) == 2 and all(t.get('spid') == shape_id for t in targets)
        transition = slide.find('p:transition', NS)
        assert transition.get('advClick') == '1' and transition.get('advTm') is None
    all_media = []
    for part, data in parts.items():
        if not (part.startswith('ppt/slides/') and part.endswith('.xml') and '/_rels/' not in part):
            continue
        slide = parse(data)
        media_pictures = [pic for pic in slide.findall('.//p:pic', NS) if pic.find('.//p14:media', NS) is not None]
        if not media_pictures:
            continue
        relations = {r.get('Id'):r for r in parse(parts[rels_part(part)])}
        for pic in media_pictures:
            media = pic.find('.//p14:media', NS)
            video = pic.find('p:nvPicPr/p:nvPr/a:videoFile', NS)
            assert video is not None, f'Media picture lacks videoFile: {part}'
            media_relation = relations[media.get(q('r','embed'))]
            video_relation = relations[video.get(q('r','link'))]
            assert media_relation.get('Type') == MEDIA_REL and video_relation.get('Type') == VIDEO_REL
            assert media_relation.get('TargetMode') != 'External' and video_relation.get('TargetMode') != 'External'
            target = target_part(part, media_relation.get('Target'))
            assert target == target_part(part, video_relation.get('Target')) and target in parts
            props = pic.find('p:nvPicPr/p:cNvPr', NS)
            all_media.append({'slide_part':part, 'shape_name':props.get('name'),
                              'shape_id':props.get('id'), 'video_part':target,
                              'bytes':len(parts[target]), 'sha256':hashlib.sha256(parts[target]).hexdigest()})
    if expected_total_video_count is not None:
        assert len(all_media) == expected_total_video_count, f'Expected {expected_total_video_count} total videos, found {len(all_media)}'
    return {'embedded_video_count':len(all_media), 'newly_embedded_video_count':len(items),
            'all_media_inventory':all_media, 'all_media_bytes_match_sources':True,
            'media_start':'presenter next click in main sequence', 'play_count':1,
            'media_fill':'hold', 'slide_advance':'manual',
            'powerpoint_playback_verified':False}


def embed_videos(input_path, mapping, output_path, ffprobe=FFPROBE, expected_total_video_count=None):
    input_path, output_path = Path(input_path).resolve(), Path(output_path).resolve()
    if input_path == output_path:
        raise ValueError('Output must be separate from the candidate input')
    if len({m['slide_part'].lstrip('/') for m in mapping}) != len(mapping):
        raise ValueError('One video per slide is supported')
    with zipfile.ZipFile(input_path) as z:
        if z.testzip() is not None:
            raise ValueError('Input ZIP failed its CRC check')
        infos = z.infolist()
        if len(infos) != len({i.filename for i in infos}):
            raise ValueError('Input ZIP has duplicate parts')
        parts = {i.filename:z.read(i) for i in infos}
    original_hashes = {n:hashlib.sha256(data).hexdigest() for n,data in parts.items()}
    records = [embed_one(parts, m, i+1, ffprobe) for i,m in enumerate(mapping)]
    content_types = parse(parts['[Content_Types].xml'])
    existing = [n for n in content_types if n.get('Extension') == 'mp4']
    if existing:
        if any(n.get('ContentType') != 'video/mp4' for n in existing):
            raise ValueError('Input MP4 content type conflicts with video/mp4')
    else:
        sub(content_types, 'ct', 'Default', Extension='mp4', ContentType='video/mp4')
    parts['[Content_Types].xml'] = serialize(content_types)
    checks = validate(parts, records, expected_total_video_count)
    edited = {'[Content_Types].xml'} | {n for r in records for n in (r['slide_part'], rels_part(r['slide_part']))}
    for part, digest in original_hashes.items():
        if part not in edited:
            assert hashlib.sha256(parts[part]).hexdigest() == digest, f'Unrelated input part changed: {part}'
    checks['all_unrelated_input_parts_preserved'] = True
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_suffix('.partial.pptx')
    with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        original = {info.filename for info in infos}
        for info in infos:
            z.writestr(info, parts[info.filename])
        for name in parts.keys() - original:
            z.writestr(name, parts[name], compress_type=zipfile.ZIP_STORED if name.endswith('.mp4') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(temp) as z:
        assert z.testzip() is None, 'Output ZIP failed its CRC check'
        validate({n:z.read(n) for n in z.namelist()}, records, expected_total_video_count)
    temp.replace(output_path)
    return {'input':str(input_path), 'output':str(output_path),
            'output_bytes':output_path.stat().st_size,
            'output_sha256':hashlib.sha256(output_path.read_bytes()).hexdigest(),
            'checks':checks, 'videos':records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--mapping', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--ffprobe', type=Path, default=FFPROBE)
    parser.add_argument('--expected-total-video-count', type=int)
    args = parser.parse_args()
    mapping = json.loads(args.mapping.read_text(encoding='utf-8-sig'))
    if isinstance(mapping, dict):
        mapping = mapping['videos']
    result = embed_videos(args.input, mapping, args.output, args.ffprobe, args.expected_total_video_count)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
