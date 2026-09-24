"""Render journal Figure 1. Six vector schematics and unaltered detector pixels.

Only the decorative border/shadow of the 3D-powder raster is cropped away.
The reciprocal panels share one camera, geometry, scale, and placement.
"""
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
HERE=ROOT/'output/figure1_journal'
OUT=ROOT/'figures/intro/orientational_limits_journal.pdf'
HERE.mkdir(parents=True,exist_ok=True)
for n,f in [('Sans','DejaVuSans.ttf'),('Sans-Bold','DejaVuSans-Bold.ttf'),('Sans-Oblique','DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(n,str(HERE/'fonts'/f)))
INK='#151515'; TEAL='#087D88'; AMBER='#C17A24'; BLUE='#2467A5'
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
def label(d,p,t,size=11,fill=INK,bold=False,italic=False):
    d.add(String(*p,t,fontName='Sans-Bold' if bold else ('Sans-Oblique' if italic else 'Sans'),fontSize=size,fillColor=color(fill)))
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
RECIP_YAW,RECIP_ELEV=-35,18
PQ,DQ=camera(RECIP_YAW,RECIP_ELEV)
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
            rgb=np.array([160,178,180])*bright+255*(1-bright)*.4
            fill='#'+''.join(f'{int(v):02x}' for v in rgb)
            faces.append((np.mean(xyz,axis=0)@DR,xyz,fill))
        normals.append((center,R,size,thick))
    for _,xyz,fill in sorted(faces,key=lambda a:a[0]): path(d,proj(xyz),'#53636A',1.0,fill)
    for center,R,size,thick in normals:
        top=center+R@np.array([0,0,thick/2+.02])
        length=.86 if kind=='single' else .53
        arrow(d,proj(top),proj(top+R[:,2]*length),INK,1.6,4.6)
        if kind!='random':
            start=top+R[:,0]*(-size*.22)
            arrow(d,proj(start),proj(start+R[:,0]*(size*.70)),AMBER,1.6,4.3)
        if kind=='single':
            label(d,proj(top+R[:,2]*length)+[5,-1],'c',12,INK,italic=True)
            label(d,proj(start+R[:,0]*(size*.70))+[5,-2],'a',12,AMBER,italic=True)
            arrow(d,proj(top),proj(top+R[:,1]*.75),TEAL,1.5,4.2)
            label(d,proj(top+R[:,1]*.75)+[-10,2],'b',12,TEAL,italic=True)
    return d

K=2.8; alpha=np.deg2rad(35)
ki=np.array([K*np.cos(alpha),0,-K*np.sin(alpha)])
C=-ki; RING=1.8; CZ=K*np.sin(alpha)
levels=[CZ]
scale=26; origin=np.array([151,59])
proj=lambda p: np.asarray(p)@PQ.T*scale+origin
theta=np.linspace(0,2*np.pi,241)
audits=[]
point_sets={}
drawn_geometry={}

def depth_curve(d,xyz,center,stroke,width=1.2):
    """Wireframe visibility is measured from its own sphere center."""
    front=((xyz-center)@DQ)>=0
    starts=np.r_[0,np.flatnonzero(front[1:]!=front[:-1])+1,len(xyz)-1]
    for start,end in zip(starts[:-1],starts[1:]):
        if end<=start: continue
        path(d,proj(xyz[start:end+1]),stroke,width if front[start] else width*.75,
             opacity=1 if front[start] else .62,dash=None if front[start] else [4,3])
    return front

def horizontal_circle(center,radius):
    return np.column_stack([radius*np.cos(theta),radius*np.sin(theta),np.zeros(len(theta))])+center

def ring_intersections(z):
    qx=(2*CZ*z-RING**2-z*z)/(2*ki[0])
    assert abs(qx)<RING
    qy=np.sqrt(RING**2-qx*qx)
    return np.array([[qx,-qy,z],[qx,qy,z]])

PAIR=ring_intersections(CZ)
G=PAIR[1]
# One reciprocal-lattice basis supplies the displayed point and both orientational
# averages. The selected point is (100)+(001), not a freely positioned marker.
avec=np.array([G[0],G[1],0.])
bvec=np.array([-G[1],G[0],0.])
cvec=np.array([0.,0.,CZ])
def sphere(d,center,radius,fill,stroke,opacity=.12,guides=True):
    cp=proj(center)
    d.add(Circle(*cp,radius*scale,fillColor=color(fill),fillOpacity=opacity,
                 strokeColor=color(stroke),strokeWidth=1.3,strokeOpacity=.85))
    for a,b in ([(0,1)] if guides else []):
        xyz=np.zeros((len(theta),3)); xyz[:,a]=radius*np.cos(theta); xyz[:,b]=radius*np.sin(theta)
        path(d,proj(xyz+center),stroke,1.0,opacity=.45,dash=[3,3])
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
    sphere(d,C,K,'#83BDE1',BLUE,.035,guides=False)
    # The xz meridian passes through O; the horizontal great circle contains
    # the selected reflection and both ring/sphere crossings exactly.
    meridian=C+K*np.column_stack([np.cos(theta),np.zeros(len(theta)),np.sin(theta)])
    depth_curve(d,meridian,C,BLUE,.8)
    if kind!='powder': depth_curve(d,horizontal_circle(C,K),C,BLUE,1.2)
    qz=np.array([0,0,4.25])
    arrow(d,proj([0,0,0]),proj(qz),INK,1.0,3.8)
    qp=proj(qz)+[4,-3]
    label(d,qp,'Q',20,INK,italic=True); label(d,qp+[15,-3],'z',13,INK)
    arrow(d,proj(C),proj([0,0,0]),BLUE,1.3,4.5)
    if kind=='single':
        kp=proj(C)+[-27,8]
        label(d,kp,'k',20,BLUE,bold=True); label(d,kp+[14,-3],'i',13,BLUE)
    if kind=='single':
        qs=[m*avec+n*bvec+l*cvec for l in [0,1,2]
            for m,n in [(-1,0),(1,0),(0,-1),(0,1),(0,0)]
            if not (m==n==0 and l==2)]
        point_sets['b']=qs
        drawn_geometry['lattice_points']=np.array(qs)
        for q in sorted(qs,key=lambda q:np.dot(q,DQ)):
            if np.linalg.norm(q)<1e-10: continue
            selected=abs(np.linalg.norm(np.array(q)-C)-K)<1e-10
            dot(d,proj(q),4.7 if selected else 2.9,INK if selected else TEAL,'#FFFFFF',.8)
        selected=np.array([q for q in qs if np.linalg.norm(q)>1e-10 and abs(np.linalg.norm(q-C)-K)<1e-10])
        assert selected.shape==(1,3) and np.allclose(selected[0],G,rtol=0,atol=1e-12)
        audits.append({'kind':'single','ewald_error':float(abs(np.linalg.norm(G-C)-K)),
                       'basis_error':float(np.linalg.norm(G-avec-cvec)),'selected_nonzero_points':len(selected)})
    elif kind=='powder':
        radius=np.linalg.norm(G)
        sphere(d,np.zeros(3),radius,TEAL,TEAL,.03,guides=False)
        depth_curve(d,horizontal_circle(np.zeros(3),radius),np.zeros(3),TEAL,.85)
        points=selected_circle(radius)
        drawn_geometry['shell_intersection']=points
        # Front/back here is relative to the Ewald sphere, not the powder-shell
        # center. Those centers differ, so the old visibility test was invalid.
        drawn_geometry['shell_front_ewald']=depth_curve(d,points,C,INK,2.1)
    else:
        point_sets['g']=[[0,0,0]]+PAIR.tolist()
        ring=horizontal_circle(np.array([0,0,CZ]),RING)
        drawn_geometry['ring']=ring
        drawn_geometry['ring_intersections']=PAIR
        drawn_geometry['ring_plane_ewald_section']=horizontal_circle(C,K)
        path(d,proj(ring),TEAL,2.0)
        audits.append({'kind':'ring','height':CZ,'ewald_error':float(np.max(np.abs(np.linalg.norm(PAIR-C,axis=1)-K))),
                       'ring_error':float(np.max(np.abs(np.linalg.norm(PAIR[:,:2],axis=1)-RING))),
                       'plane_error':float(np.max(np.abs(PAIR[:,2]-CZ))),
                       'shared_shell_error':float(np.max(np.abs(np.linalg.norm(PAIR,axis=1)-np.linalg.norm(G))))})
        for q in PAIR: dot(d,proj(q),4.7,INK,'#FFFFFF',.8)
    dot(d,proj([0,0,0]),2.0,INK)
    if kind=='single': label(d,proj([0,0,0])+[6,-20],'O',18)
    return d

drawings={'a':specimen('single'),'b':reciprocal('single'),'c':specimen('random'),
          'd':reciprocal('powder'),'f':specimen('aligned'),'g':reciprocal('rings')}
for letter,d in drawings.items(): renderSVG.drawToFile(d,str(HERE/f'panel_{letter}.svg'))
W,H=648,465
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Orientational limits in real, reciprocal, and detector space')
def txt(x,top,s,size=12,bold=False,col=INK):
    c.setFillColor(color(col)); c.setFont('Sans-Bold' if bold else 'Sans',size)
    c.drawString(x,H-top-size*.82,s)
for x,t in [(12,'Real space'),(244,'Reciprocal space'),(470,'Detector space')]: txt(x,3,t,12,True)
sources={}
placements={}
rb=np.asarray([drawings[l].getBounds() for l in ['b','d','g']])
shared_bounds=[rb[:,0].min()-3,rb[:,1].min()-3,rb[:,2].max()+3,rb[:,3].max()+3]
detector_crops={}
for row,(top,title,letters) in enumerate(zip([24,170,316],['Single crystal','3D powder','2D powder'],[('a','b',None),('c','d','e'),('f','g','h')])):
    txt(12,top,title,11.5,True)
    for col,letter in enumerate(letters):
        if not letter: continue
        x=[12,244,470][col]; y=top+15; txt(x,y,f'({letter})',11.8,True)
        if letter in drawings:
            d=drawings[letter]
            if col==1:
                x0,y0,x1,y1=shared_bounds
            else:
                x0,y0,x1,y1=d.getBounds()
                x0-=3; y0-=3; x1+=3; y1+=3
            fw,fh=211,126
            s=min(fw/(x1-x0),fh/(y1-y0))
            px=x+(fw-s*(x1-x0))/2
            py=H-y-fh+(fh-s*(y1-y0))/2
            c.saveState(); c.translate(px-s*x0,py-s*y0); c.scale(s,s)
            renderPDF.draw(d,c,0,0); c.restoreState()
            placements[letter]={'content_bounds':[x0,y0,x1,y1],'scale':s,'row_top':top,
                                'origin_in_row':[px-s*x0,(H-py)+s*y0-top]}
        else:
            name='detector_3d_powder_hbn.png' if letter=='e' else 'detector_2d_powder_biggerB_4deg_2m.png'
            src=ROOT/'figures/intro'/name; im=Image.open(src).convert('RGBA')
            # These exact bounds retain every pixel of the opaque detector face.
            # Only the external gray frame and shadow of panel (e) are excluded.
            bounds=(21,21,411,419) if letter=='e' else (0,0,im.width,im.height)
            original=im
            im=im.crop(bounds)
            assert np.array_equal(np.asarray(im),np.asarray(original)[bounds[1]:bounds[3],bounds[0]:bounds[2]])
            detector_crops[letter]=list(bounds)
            s=min(124/im.width,124/im.height); ww,hh=im.width*s,im.height*s
            c.drawImage(ImageReader(im),x+31+(124-ww)/2,H-y-126+(124-hh)/2,ww,hh,mask='auto')
            sources[name]=hashlib.sha256(src.read_bytes()).hexdigest()
c.showPage(); c.save()
np.savez(HERE/'geometry_arrays.npz',**drawn_geometry,ki=ki,ewald_center=C,
         ewald_radius=K,selected_G=G,lattice_basis=np.array([avec,bvec,cvec]),
         projection=PQ,view_direction=DQ)
assert all(v['ewald_error']<1e-12 for v in audits)
spacing={}
for letter,qs in point_sets.items():
    p=proj(qs)*placements[letter]['scale']
    distances=np.linalg.norm(p[:,None,:]-p[None,:,:],axis=2)
    np.fill_diagonal(distances,np.inf)
    spacing[letter]={'minimum_point_center_distance_export_pt':float(distances.min())}
caption=('Figure 1. Orientational limits in real, reciprocal, and detector space. '
'The six vector schematics are generic teaching geometry, not material-specific reflection assignments. '
'(a,b) One crystal orientation produces discrete reciprocal-lattice points. '
'(c-e) Random 3D orientations spread each reflection over a spherical shell, whose Ewald intersection projects to a Debye-Scherrer ring. '
'(f-h) Aligned crystal normals with random in-plane azimuth give off-axis reciprocal rings and paired Ewald intersections. '
'Black real-space arrows denote crystal normals. Amber arrows show an in-plane direction. '
'The blue sphere is the Ewald sphere centered at minus the incident wavevector ki and passing through reciprocal origin O. '
'The wavevector and origin labels in (b) apply also to (d,g). '
'Qz is the reciprocal axis along the reference film normal. Teal and amber distinguish selected reflection loci. '
'Dark dots in (b,g) and dark shell-intersection curves in (d) mark elastically selected scattering. '
'The same selected off-axis reflection generates the shell in (d) and ring in (g). '
'Blue great circles define the Ewald surface, including its section through the ring plane. '
'Dashed black shell-intersection segments lie on the rear Ewald hemisphere. '
'Axial 00L scattering is omitted from these representative orientational averages. '
'Original detector examples (e,h) retain their source pixels and independent display colors. '
'They illustrate morphology rather than a matched intensity or material comparison. No single-crystal detector image is supplied.')
(HERE/'caption.txt').write_text(caption,encoding='utf-8')
(HERE/'verification.json').write_text(json.dumps({'geometry':audits,'projected_spacing':spacing,'detector_source_sha256':sources,'detector_crops':detector_crops,
    'layout':{'width':W,'height':H,'previous_width':720,'previous_height':684,'placements':placements},
    'schematic_parameters':{'k':K,'incidence_degrees':float(np.rad2deg(alpha)),'ring_radius':RING,'heights':levels,
                            'view_yaw_degrees':RECIP_YAW,'view_elevation_degrees':RECIP_ELEV,
                            'selected_G':G.tolist(),'paired_intersections':PAIR.tolist(),
                            'lattice_basis':np.array([avec,bvec,cvec]).tolist()},
    'scope':'Generic vector schematic. No gray explanatory text. No fitted parameters or new detector evidence.'},indent=2),encoding='utf-8')
print(OUT)
print('Maximum Ewald residual:',max(v['ewald_error'] for v in audits))
assert placements['b']['scale']==placements['d']['scale']==placements['g']['scale']
assert np.allclose([placements[l]['origin_in_row'] for l in ['b','d','g']],
                   placements['b']['origin_in_row'],rtol=0,atol=1e-12)
import shutil
shutil.copy2(OUT,HERE/'Figure_1_journal.pdf')
