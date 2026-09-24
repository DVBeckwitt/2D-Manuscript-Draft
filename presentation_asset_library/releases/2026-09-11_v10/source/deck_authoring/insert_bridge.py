"""Insert the authored poster/media slide while preserving all existing slides."""
from pathlib import Path
import sys,zipfile,re,json,hashlib,posixpath,importlib.util
from lxml import etree as E
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd();TMP=ROOT/'build_codex/slate_talk/animated_deck_v10'
SRC=ROOT/'presentation_asset_library/releases/2026-09-10_v9/presentation/Oriented_Powder_8min_Animated_v9.pptx'
TITLE='From Bragg peaks to diffraction cylinders'
P='http://schemas.openxmlformats.org/presentationml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
AP='http://schemas.openxmlformats.org/officeDocument/2006/extended-properties';VT='http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
def read(p):
    with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def xml(b):return E.fromstring(b)
def serial(e):return E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def relname(p):return posixpath.join(posixpath.dirname(p),'_rels',posixpath.basename(p)+'.rels')
def resolve(p,t):return t.lstrip('/') if t.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(p),t))
def rels(parts,p):return xml(parts[relname(p)])
assert sha(SRC.read_bytes())=='0feca65d8e57c764666012cc75cd880da660fd1fea12eedba0cec69193c2cec3'
modspec=importlib.util.spec_from_file_location('video',TMP.parent/'animated_deck/embed_videos.py')
video=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(video)
poster=read(TMP/'bridge_slide.pptx')
pics=xml(poster['ppt/slides/slide1.xml']).findall('.//{'+P+'}pic');assert len(pics)==1
sid=pics[0].find('{'+P+'}nvPicPr/{'+P+'}cNvPr').get('id')
mapping=[{'slide_part':'ppt/slides/slide1.xml','shape_id':sid,'shape_name':'Cylinder bridge v3',
          'video_path':str(ROOT/'output/cylinder_bridge_v3/Cylinder_Bridge.mp4')}]
vr=video.embed_videos(TMP/'bridge_slide.pptx',mapping,TMP/'bridge_with_video.pptx',Path('C:/ffmpeg/bin/ffprobe.exe'),1)
(TMP/'new_video_validation.json').write_text(json.dumps(vr,indent=2)+'\n')
source=read(SRC);out=dict(source);donor=read(TMP/'bridge_with_video.pptx')
pres=xml(source['ppt/presentation.xml']);pr=rels(source,'ppt/presentation.xml');byrid={r.get('Id'):r for r in pr}
ids=pres.find('{'+P+'}sldIdLst');assert len(ids)==25
oldslides=[resolve('ppt/presentation.xml',byrid[i.get('{'+R+'}id')].get('Target')) for i in ids]
base_layout=next(resolve(oldslides[4],r.get('Target')) for r in rels(source,oldslides[4]) if r.get('Type').endswith('/slideLayout'))
base_notesmaster=next(resolve('ppt/presentation.xml',r.get('Target')) for r in pr if r.get('Type').endswith('/notesMaster'))
next_num=max(int(re.search(r'slide(\d+)\.xml$',n).group(1)) for n in source if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))+1
newslide=f'ppt/slides/slide{next_num}.xml';newnotes=f'ppt/notesSlides/notesSlide{next_num}.xml'
mapping={'ppt/slides/slide1.xml':newslide,'ppt/notesSlides/notesSlide1.xml':newnotes,
         'ppt/slideLayouts/slideLayout1.xml':base_layout,'ppt/notesMasters/notesMaster1.xml':base_notesmaster}
for n in donor:
    if n.startswith('ppt/media/'):
        mapping[n]='ppt/media/cylinder_v3_'+posixpath.basename(n)
        assert mapping[n] not in out
        out[mapping[n]]=donor[n]
for old,new in [('ppt/slides/slide1.xml',newslide),('ppt/notesSlides/notesSlide1.xml',newnotes)]:
    e=xml(donor[old])
    if old.endswith('/slide1.xml'):e.find('{'+P+'}cSld').set('name',TITLE)
    out[new]=serial(e)
    rs=rels(donor,old)
    for r in rs:
        assert r.get('TargetMode')!='External'
        dest=resolve(old,r.get('Target'));assert dest in mapping,dest
        r.set('Target',posixpath.relpath(mapping[dest],posixpath.dirname(new)))
    out[relname(new)]=serial(rs)
rid='rIdCylinderBridgeV3';assert rid not in byrid
newid=E.Element('{'+P+'}sldId',id=str(max(int(e.get('id')) for e in ids)+1))
newid.set('{'+R+'}id',rid);ids.insert(18,newid)
E.SubElement(pr,'{'+PR+'}Relationship',Id=rid,Type=R+'/slide',Target=posixpath.relpath(newslide,'ppt'))
out['ppt/presentation.xml']=serial(pres);out['ppt/_rels/presentation.xml.rels']=serial(pr)
ct=xml(source['[Content_Types].xml'])
for n,kind in [(newslide,'slide'),(newnotes,'notesSlide')]:
    E.SubElement(ct,'{'+CT+'}Override',PartName='/'+n,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
out['[Content_Types].xml']=serial(ct)
app=xml(source['docProps/app.xml'])
for name,value in [('Slides','26'),('Notes','26'),('MMClips','8')]:app.find('{'+AP+'}'+name).text=value
vec=app.find('{'+AP+'}TitlesOfParts/{'+VT+'}vector');assert len(vec)==25
title=E.Element('{'+VT+'}lpstr');title.text=TITLE;vec.insert(18,title);vec.set('size','26')
app.find('{'+AP+'}HeadingPairs/{'+VT+'}vector/{'+VT+'}variant/{'+VT+'}i4').text='26'
out['docProps/app.xml']=serial(app)
allowed={'ppt/presentation.xml','ppt/_rels/presentation.xml.rels','[Content_Types].xml','docProps/app.xml'}
changed=[n for n in source if source[n]!=out[n]];assert set(changed)==allowed
assert all(out[n]==source[n] for n in oldslides)
for n,b in out.items():
    if n.endswith('.rels'):
        owner='' if n=='_rels/.rels' else posixpath.join(posixpath.dirname(posixpath.dirname(n)),posixpath.basename(n)[:-5])
        for r in xml(b):
            if r.get('TargetMode')!='External':assert resolve(owner,r.get('Target')) in out,(n,r.attrib)
candidate=TMP/'candidate.pptx'
with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for n,b in out.items():z.writestr(n,b)
report={'source':str(SRC),'candidate':str(candidate),'source_sha256':sha(SRC.read_bytes()),'candidate_sha256':sha(candidate.read_bytes()),
        'insertion_index':19,'new_slide_part':newslide,'new_notes_part':newnotes,'title':TITLE,
        'old_slide_order_preserved':True,'all_old_slides_notes_charts_workbooks_media_byte_preserved':True,
        'changed_existing_parts':changed,'added_parts':sorted(set(out)-set(source)),
        'new_movie_sha256':vr['videos'][0]['sha256'],'slide_mapping':[{'old':i,'new':i if i<19 else i+1,'part':s} for i,s in enumerate(oldslides,1)]}
(TMP/'insertion_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='slide_mapping'},indent=2))
