"""Vector redraw of six schematics. Original detector pixels are retained."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Polygon, PolyLine, Circle, String
from reportlab.graphics import renderPDF, renderSVG

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'output/figure1_compact_reference'
HERE.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'figures/intro/orientational_limits_compact.pdf'
for n,f in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(n,str(Path('C:/Windows/Fonts')/f)))
INK='#183442'; TEAL='#15877E'; AMBER='#DA942C'; BLUE='#428EC1'
def color(x): return HexColor(x)
def path(d,xy,stroke=INK,width=1,fill=None,opacity=1,dash=None):
    pts=np.asarray(xy).reshape(-1).tolist()
    if fill is None:
        s=PolyLine(pts,strokeColor=color(stroke),strokeWidth=width,strokeOpacity=opacity)
    else:
        s=Polygon(pts,strokeColor=color(stroke),strokeWidth=width,fillColor=color(fill),fillOpacity=opacity)
    if dash: s.strokeDashArray=dash
    d.add(s)
def dot(d,p,r=2.3,fill=INK,edge=None,width=.6):
    d.add(Circle(*p,r,fillColor=color(fill),strokeColor=color(edge or fill),strokeWidth=width))
def label(d,p,t,size=10,fill=INK,bold=False):
    d.add(String(*p,t,fontName='Arial-Bold' if bold else 'Arial',fontSize=size,fillColor=color(fill)))
def arrow(d,a,b,stroke=INK,width=1.3,head=4):
    a,b=np.array(a),np.array(b); path(d,[a,b],stroke,width)
    u=(b-a)/np.linalg.norm(b-a); v=np.array([-u[1],u[0]])
    path(d,[b,b-head*u+.43*head*v,b-head*u-.43*head*v],stroke,.3,stroke)
def camera(yaw,elev):
    t,e=np.deg2rad([yaw,elev])
    u=np.array([np.cos(t),np.sin(t),0])
    v=np.array([-np.sin(t)*np.sin(e),np.cos(t)*np.sin(e),np.cos(e)])
    return np.array([u,v]),np.cross(u,v)
PR,DR=camera(-40,27)
PQ,DQ=camera(40,20)
def rotz(t):
    t=np.deg2rad(t); c,s=np.cos(t),np.sin(t)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def rotx(t):
    t=np.deg2rad(t); c,s=np.cos(t),np.sin(t)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])

def specimen(kind):
    d=Drawing(230,174)
    proj=lambda p: np.asarray(p)@PR.T*40+np.array([114,84])
    base=np.array([[-2.1,-1.45,-.12],[2.1,-1.45,-.12],[2.1,1.45,-.12],[-2.1,1.45,-.12]])
    bottom=base.copy(); bottom[:,2]-=.12
    for i in range(4):
        j=(i+1)%4
        path(d,proj([bottom[i],bottom[j],base[j],base[i]]),'#95ADB7',.6,'#D9E4E8')
    path(d,proj(base),'#95ADB7',.8,'#F1F5F6')
    if kind=='single': grains=[(np.array([0.,0.,.34]),np.eye(3),1.65,.72)]
    else:
        positions=[(-1.28,-.76),(-.12,-.78),(1.12,-.7),(-1.18,.52),(.0,.5),(1.22,.54)]
        yaw=[12,72,138,44,116,163]
        tilts=[(64,38),(-53,20),(38,-56),(76,10),(-34,48),(44,-42)]
        grains=[]
        for (x,y),az,(tx,ty) in zip(positions,yaw,tilts):
            R=rotz(az)
            if kind=='random': R=R@rotx(tx)@rotz(ty)
            local=np.array([[sx*.4,sy*.4,sz*.1] for sx in [-1,1] for sy in [-1,1] for sz in [-1,1]])
            z=.02-np.min((local@R.T)[:,2])
            grains.append((np.array([x,y,z]),R,.80,.20))
    faces=[]; normals=[]
    for center,R,size,thick in grains:
        verts=np.array([[x*size/2,y*size/2,z*thick/2] for x,y,z in
                        [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
        verts=verts@R.T+center
        for ids,n in [([0,3,2,1],[0,0,-1]),([4,5,6,7],[0,0,1]),([0,1,5,4],[0,-1,0]),
                      ([1,2,6,5],[1,0,0]),([2,3,7,6],[0,1,0]),([3,0,4,7],[-1,0,0])]:
            normal=R@np.array(n)
            if normal@DR<=0: continue
            xyz=verts[ids]
            bright=float(np.clip(.75+.22*(normal@np.array([-.3,-.5,.81])),.45,.98))
            rgb=np.array([100,190,166])*bright+255*(1-bright)*.4
            fill='#'+''.join(f'{int(v):02x}' for v in rgb)
            faces.append((np.mean(xyz,axis=0)@DR,xyz,fill))
        normals.append((center,R,size,thick))
    for _,xyz,fill in sorted(faces,key=lambda a:a[0]): path(d,proj(xyz),'#236457',.85,fill)
    for center,R,size,thick in normals:
        top=center+R@np.array([0,0,thick/2+.02])
        length=.86 if kind=='single' else .53
        arrow(d,proj(top),proj(top+R[:,2]*length),INK,1.6,4.6)
        if kind!='random':
            start=top+R[:,0]*(-size*.22)
            arrow(d,proj(start),proj(start+R[:,0]*(size*.70)),AMBER,1.6,4.3)
        if kind=='single':
            label(d,proj(top+R[:,2]*length)+[5,-1],'c',11,INK,True)
            label(d,proj(start+R[:,0]*(size*.70))+[5,-2],'a',11,AMBER,True)
            arrow(d,proj(top),proj(top+R[:,1]*.75),TEAL,1.5,4.2)
            label(d,proj(top+R[:,1]*.75)+[-10,2],'b',11,TEAL,True)
    return d

K=2.8; alpha=np.deg2rad(20)
ki=np.array([K*np.cos(alpha),0,-K*np.sin(alpha)])
C=-ki; RING=1.1; CZ=K*np.sin(alpha)
levels=[CZ,2*CZ]
scale=26; origin=np.array([151,59])
proj=lambda p: np.asarray(p)@PQ.T*scale+origin
theta=np.linspace(0,2*np.pi,241)
audits=[]
def sphere(d,center,radius,fill,stroke,opacity=.12):
    cp=proj(center)
    d.add(Circle(*cp,radius*scale,fillColor=color(fill),fillOpacity=opacity,
                 strokeColor=color(stroke),strokeWidth=.85,strokeOpacity=.7))
    for a,b in [(0,1),(0,2)]:
        xyz=np.zeros((len(theta),3)); xyz[:,a]=radius*np.cos(theta); xyz[:,b]=radius*np.sin(theta)
        path(d,proj(xyz+center),stroke,.55,opacity=.32,dash=[2,2])
def selected_circle(radius):
    n=C/K; offset=radius**2/(2*K); ctr=offset*n
    a=np.cross(n,[0,1,0]); a/=np.linalg.norm(a); b=np.cross(n,a)
    rho=np.sqrt(radius**2-offset**2)
    xyz=ctr+rho*(np.cos(theta)[:,None]*a+np.sin(theta)[:,None]*b)
    audits.append({'kind':'shell','radius':radius,'ewald_error':float(np.max(np.abs(np.linalg.norm(xyz-C,axis=1)-K))),
                   'shell_error':float(np.max(np.abs(np.linalg.norm(xyz,axis=1)-radius)))})
    return xyz
def reciprocal(kind):
    d=Drawing(230,174)
    sphere(d,C,K,'#83BDE1',BLUE,.17)
    qz=np.array([0,0,3.35])
    arrow(d,proj([0,0,0]),proj(qz),'#668897',.8,3)
    qp=proj(qz)+[4,-3]
    label(d,qp,'Q',9,INK); label(d,qp+[7,-2],'z',6.5,INK)
    arrow(d,proj(C),proj([0,0,0]),BLUE,1.3,4.5)
    kp=(proj(C)+proj([0,0,0]))/2+[-16,-8]
    label(d,kp,'k',9,BLUE); label(d,kp+[5,-2],'i',6.5,BLUE)
    if kind=='single':
        qs=[[x,y,z] for z in [0,CZ,2*CZ] for x,y in [(-RING,0),(RING,0),(0,-RING),(0,RING),(0,0)]]
        for q in sorted(qs,key=lambda q:np.dot(q,DQ)):
            if np.linalg.norm(q)<1e-10: continue
            selected=abs(np.linalg.norm(np.array(q)-C)-K)<1e-10
            dot(d,proj(q),3.5 if selected else 2.25,INK if selected else '#62AA9E','#FFFFFF',.55)
    elif kind=='powder':
        for z,col in zip(levels,[TEAL,AMBER]):
            radius=np.hypot(RING,z)
            sphere(d,np.zeros(3),radius,col,col,.055)
            points=selected_circle(radius); vis=(points@DQ)>0
            for i in range(len(points)-1):
                if vis[i] or i%4<2: path(d,proj(points[i:i+2]),col,1.8 if vis[i] else .9,opacity=1 if vis[i] else .60)
    else:
        for z,col in zip(levels,[TEAL,AMBER]):
            ring=np.column_stack([RING*np.cos(theta),RING*np.sin(theta),np.full(len(theta),z)])
            path(d,proj(ring),col,1.5)
            qx=(2*CZ*z-RING**2-z*z)/(2*ki[0]); qy=np.sqrt(RING**2-qx*qx)
            points=np.array([[qx,-qy,z],[qx,qy,z]])
            audits.append({'kind':'ring','height':z,'ewald_error':float(np.max(np.abs(np.linalg.norm(points-C,axis=1)-K))),
                           'ring_error':float(np.max(np.abs(np.linalg.norm(points[:,:2],axis=1)-RING)))})
            for q in points: dot(d,proj(q),3.25,INK,'#FFFFFF',.65)
        for z in levels: dot(d,proj([0,0,z]),3 if abs(z-2*CZ)<1e-10 else 2.2,INK if abs(z-2*CZ)<1e-10 else '#8B65A7','#FFFFFF',.4)
    dot(d,proj([0,0,0]),2.0,INK); label(d,proj([0,0,0])+[5,-12],'O',8.7)
    return d

drawings={'a':specimen('single'),'b':reciprocal('single'),'c':specimen('random'),
          'd':reciprocal('powder'),'f':specimen('aligned'),'g':reciprocal('rings')}
for letter,d in drawings.items(): renderSVG.drawToFile(d,str(HERE/f'panel_{letter}.svg'))
W,H=620,534
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Figure 1: compact vector layout')
def txt(x,top,s,size=12,bold=False,col=INK):
    c.setFillColor(color(col)); c.setFont('Arial-Bold' if bold else 'Arial',size)
    c.drawString(x,H-top-size*.82,s)
def rule(top):
    c.setStrokeColor(color('#D9E3E7')); c.setLineWidth(.65); c.line(12,H-top,608,H-top)
for x,t in [(12,'Crystallite orientations'),(232,'Reciprocal-space geometry'),(438,'Detector pattern')]: txt(x,6,t,13,True)
rule(27)
sources={}
placements={}
for row,(top,title,letters) in enumerate(zip([34,200,366],['Single crystal','3D powder','2D powder'],[('a','b',None),('c','d','e'),('f','g','h')])):
    if row==2:
        c.setFillColor(color('#F0F7F7')); c.roundRect(5,H-top-164,610,169,7,fill=1,stroke=0)
        c.setFillColor(color(TEAL)); c.rect(5,H-top-164,3,169,fill=1,stroke=0)
    txt(12,top,title,14,True,TEAL if row==2 else INK)
    for col,letter in enumerate(letters):
        if not letter: continue
        x=[12,232,438][col]; y=top+18; txt(x,y,f'({letter})',11.4,True)
        if letter in drawings:
            d=drawings[letter]
            x0,y0,x1,y1=d.getBounds()
            # Fit actual vector content rather than its padded drawing canvas.
            # Padding allows for strokes and text descenders without clipping.
            x0-=3; y0-=3; x1+=3; y1+=3
            fw,fh=214,126
            s=min(fw/(x1-x0),fh/(y1-y0))
            px=x+(fw-s*(x1-x0))/2
            py=H-y-fh+(fh-s*(y1-y0))/2
            c.saveState(); c.translate(px-s*x0,py-s*y0); c.scale(s,s)
            renderPDF.draw(d,c,0,0); c.restoreState()
            placements[letter]={'content_bounds':[x0,y0,x1,y1],'scale':s}
        else:
            name='detector_3d_powder_hbn.png' if letter=='e' else 'detector_2d_powder_biggerB_4deg_2m.png'
            src=ROOT/'figures/intro'/name; im=Image.open(src).convert('RGBA')
            bounds=im.getchannel('A').getbbox(); im=im.crop(bounds)
            s=min(125/im.width,125/im.height); ww,hh=im.width*s,im.height*s
            c.drawImage(ImageReader(im),x+23+(125-ww)/2,H-y-126+(125-hh)/2,ww,hh,mask='auto')
            sources[name]=hashlib.sha256(src.read_bytes()).hexdigest()
    if row==0: txt(460,top+74,'Sparse spots',14,True)
    notes=[['Fixed crystal axes','Discrete reciprocal-lattice points',None],
           ['No preferred orientation','Spherical shells','Debye-Scherrer rings'],
           ['Common film normal','Rings about the normal axis','Paired off-specular features']][row]
    for x,n in zip([12,232,438],notes):
        if n: txt(x,top+149,n,11.1,row==2,TEAL if row==2 else INK)
    if row<2: rule(top+163)
c.showPage(); c.save()
assert all(v['ewald_error']<1e-12 for v in audits)
caption=('Figure 1. Orientational limits in real, reciprocal, and detector space. '
'The six vector schematics are generic teaching geometry, not material-specific reflection assignments. '
'(a,b) One crystal orientation produces discrete reciprocal-lattice points. '
'(c-e) Random 3D orientations spread each reflection over a spherical shell, whose Ewald intersection projects to a Debye-Scherrer ring. '
'(f-h) Aligned crystal normals with random in-plane azimuth give off-axis reciprocal rings and paired Ewald intersections. '
'Black real-space arrows denote crystal normals. Amber arrows show an in-plane direction. '
'The blue sphere is the Ewald sphere centered at minus the incident wavevector ki and passing through reciprocal origin O. '
'Qz is the reciprocal axis along the reference film normal. Teal and amber distinguish selected reflection loci. '
'Dark dots in (b,g) and colored shell-intersection curves in (d) mark elastically selected scattering. '
'Solid and dashed shell-intersection segments indicate front and back. '
'Axial reciprocal points in (g) stay on the common normal, with the upper point selected at this illustrative incidence. '
'Original detector examples (e,h) retain their source pixels and independent display colors. '
'They illustrate morphology rather than a matched intensity or material comparison. No single-crystal detector image is supplied.')
(HERE/'caption.txt').write_text(caption,encoding='utf-8')
(HERE/'verification.json').write_text(json.dumps({'geometry':audits,'detector_source_sha256':sources,
    'layout':{'width':W,'height':H,'previous_width':690,'previous_height':574,'placements':placements},
    'schematic_parameters':{'k':K,'incidence_degrees':20,'ring_radius':RING,'heights':levels},
    'scope':'Generic vector schematic. No gray explanatory text. No fitted parameters or new detector evidence.'},indent=2),encoding='utf-8')
print(OUT)
print('Maximum Ewald residual:',max(v['ewald_error'] for v in audits))

# The author selected the exact v3 artwork. Only composition may differ.
reference=ROOT/'output/figure1_redesign_v3'
source=(reference/'make_figure.py').read_text(encoding='utf-8')
current=Path(__file__).read_text(encoding='utf-8')
start='INK='; end='for letter,d in drawings.items():'
assert source[source.index(start):source.index(end)]==current[current.index(start):current.index(end)]
hashes={}
for letter in drawings:
    original=(reference/f'panel_{letter}.svg').read_bytes()
    final=(HERE/f'panel_{letter}.svg').read_bytes()
    assert final==original, f'Panel {letter} changed'
    hashes[letter]=hashlib.sha256(final).hexdigest()
report=json.loads((HERE/'verification.json').read_text(encoding='utf-8'))
report['preservation']={'source':'output/figure1_redesign_v3',
    'panel_svgs_byte_identical':True,'panel_sha256':hashes,
    'drawing_code_identical':True,'change_scope':'Panel placement, uniform panel size, margins and gaps only.'}
(HERE/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
import shutil
shutil.copy2(OUT,ROOT/'output/pdf/Figure_1_compact.pdf')
