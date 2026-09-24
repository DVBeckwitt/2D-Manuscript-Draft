"""Ideal Bragg peaks -> finite ordered rods -> cylinders -> mosaic -> Ewald.

Public rendering API (no file writes on import):
    draw_stage(ax, stage, progress=1.0, *, annotations=True, fontsize=9)
stage is 0 (near-ideal peaks to finite rod), 1 (azimuth sweep), 2 (rigid mosaic
tilt), or 3 (Ewald). Stage0 uses a continuous mean layer count returned by
opening_layer_count(p), from512 at p0 to8 at p1. Noninteger means describe a
population of adjacent integer stack thicknesses, not fractional atomic layers.
No arrow-only state appears in the animation. ideal_reference=True adds the
unchanged symbolic ideal arrows to the final static N8 comparison only.
progress is clipped to [0,1]. Annotations=False removes explanatory sentences
but keeps physical coordinate labels. An ordinary Matplotlib Axes is required.
The function clears/configures that Axes and returns its current child artists.
All stages use the same fixed orthographic camera and world viewport.
Run this file directly to regenerate the static figure, arrays and provenance.
"""
from pathlib import Path
from functools import lru_cache
import json, hashlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from matplotlib.colors import to_rgba

OUT=Path(__file__).resolve().parents[1]
N=8; R=1.; K=3.4; INCIDENCE_DEG=20.
LMIN=.15; LMAX=3.55
SIGMA_CORE_DEG=3.; SIGMA_BROAD_DEG=9.; BROAD_FRACTION=.18; MAX_TILT_DEG=18.
N_ALPHA=12; N_AZIMUTH=32
LGRID=np.linspace(LMIN,LMAX,421)
KI=K*np.array([np.cos(np.deg2rad(INCIDENCE_DEG)),0.,-np.sin(np.deg2rad(INCIDENCE_DEG))])
CENTER=-KI
EL=np.deg2rad(20); YAW=np.deg2rad(-45)
RIGHT=np.array([np.cos(YAW),-np.sin(YAW),0.])
UP=np.array([np.sin(EL)*np.sin(YAW),np.sin(EL)*np.cos(YAW),np.cos(EL)])
INK='#243844'; TEAL='#087F8C'; AMBER='#D27A25'; GREY='#8498A4'; BLUE='#759FAF'
VIEW=(-5.82,2.55,-1.75,5.46)

def setup():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
        'svg.fonttype':'none','axes.unicode_minus':True,'savefig.facecolor':'white',
        'figure.facecolor':'white','text.color':INK,'axes.labelcolor':INK,
        'axes.linewidth':.65})

def project(q):
    a=np.asarray(q,float);return np.stack([a@RIGHT,a@UP],axis=-1)

def rod_intensity(L):
    a=np.asarray(L,float)
    return np.abs(np.exp(2j*np.pi*a[...,None]*np.arange(N)).sum(axis=-1))**2/N**2

def opening_layer_count(progress):
    """Continuous mean thickness. Inverse mean grows linearly from1/512 to1/8."""
    p=float(np.clip(progress,0,1))
    return 1/(1/512+(1/8-1/512)*p)

def finite_stack_profile(L,layers):
    """Peak-normalized coherent intensity for an integer number of unit layers.

    The period area is1/layers, not a conserved area during this teaching
    sequence. This direct-sum API is retained for independent numerical checks.
    """
    if isinstance(layers,bool) or int(layers)!=layers or layers<1:
        raise ValueError('layers must be a positive integer')
    layers=int(layers);a=np.asarray(L,float)
    return np.abs(np.exp(2j*np.pi*a[...,None]*np.arange(layers)).sum(axis=-1))**2/layers**2

def _integer_profile_fast(L,layers):
    """Equivalent integer coherent law, stable at every exact Bragg order."""
    a=np.asarray(L,float);delta=a-np.rint(a)
    return (np.sinc(int(layers)*delta)/np.sinc(delta))**2

def thickness_population_profile(L,mean_layers):
    """Incoherent intensity mixture of two real, neighboring integer stacks.

    Let mean=m+f. Population fractions are1-f and f. Intensities are mixed
    before dividing by the mixture's coherent peak, preserving unit peaks.
    """
    mean=float(mean_layers)
    if not np.isfinite(mean) or mean<1:raise ValueError('mean_layers must be finite and at least1')
    if mean==N:return rod_intensity(L)  # Bit-identical final N8 source values.
    m=int(np.floor(mean));f=mean-m
    if f==0:return _integer_profile_fast(L,m)
    low=(1-f)*m*m;high=f*(m+1)*(m+1)
    return (low*_integer_profile_fast(L,m)+high*_integer_profile_fast(L,m+1))/(low+high)

@lru_cache(maxsize=8)
def opening_profile_data(layers):
    """Dense opening-only grid resolves the narrowest512-layer curve."""
    orders=np.arange(1.,4.)
    m=int(np.floor(layers));n=m+1
    local=(orders[:,None]+np.linspace(-6/layers,6/layers,801)).ravel()
    ell=np.unique(np.r_[np.linspace(LMIN,LMAX,32769),orders,
        orders-1/m,orders+1/m,orders-1/n,orders+1/n,local])
    ell=ell[(ell>=LMIN)&(ell<=LMAX)]
    return ell,thickness_population_profile(ell,layers)

def contrast(s):
    return np.arcsinh(np.maximum(s,0)/.02)/np.arcsinh(50.)

def rotation(alpha,beta):
    # Rz(beta) Ry(alpha) Rz(-beta), rotation of the entire reciprocal cylinder.
    b=np.array([-np.sin(beta),np.cos(beta),0.]);x,y,z=b
    cross=np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])
    return np.eye(3)*np.cos(alpha)+(1-np.cos(alpha))*np.outer(b,b)+np.sin(alpha)*cross

@lru_cache(None)
def orientation_states():
    x,w=np.polynomial.legendre.leggauss(N_ALPHA)
    a=(x+1)*np.deg2rad(MAX_TILT_DEG)/2;da=w*np.deg2rad(MAX_TILT_DEG)/2
    gauss=lambda sig:np.exp(-.5*(a/np.deg2rad(sig))**2)
    core=gauss(SIGMA_CORE_DEG);broad=gauss(SIGMA_BROAD_DEG)
    measure=2*np.pi*np.sin(a)*da
    core/=np.sum(core*measure);broad/=np.sum(broad*measure)
    radial=((1-BROAD_FRACTION)*core+BROAD_FRACTION*broad)*measure
    return tuple((float(aa),float(2*np.pi*j/N_AZIMUTH),float(mass/N_AZIMUTH))
        for aa,mass in zip(a,radial) for j in range(N_AZIMUTH))

def exact_locus(U,L=LGRID):
    """Both analytic azimuth roots at every continuous intrinsic L.

    q=U(R cosβ,R sinβ,L). Elastic restriction solves A cosβ+B sinβ=C.
    Every in-window root is kept. None is admitted using a physical tolerance.
    """
    n=U[:,2];u=U[:,0];v=U[:,1]
    A=2*R*(KI@u);B=2*R*(KI@v);C=-(L*L+R*R+2*L*(KI@n))
    amplitude=np.hypot(A,B); valid=np.abs(C)<=amplitude
    phase=np.arctan2(B,A);delta=np.arccos(np.clip(C/amplitude,-1,1))
    result=[]
    for sign in [-1,1]:
        beta=phase+sign*delta
        q=(R*np.cos(beta))[:,None]*u+(R*np.sin(beta))[:,None]*v+L[:,None]*n
        result.append((q,valid.copy()))
    return result

@lru_cache(None)
def selected_population():
    return tuple((exact_locus(rotation(a,b)),weight) for a,b,weight in orientation_states())

def _arrow(ax,a,b,color=INK,lw=1.,head=6,alpha=1):
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=color,lw=lw,
        mutation_scale=head,alpha=alpha,shrinkA=0,shrinkB=0))

def _line(ax,q,color=TEAL,lw=1,alpha=1,ls='-'):
    p=project(q);ax.plot(p[:,0],p[:,1],color=color,lw=lw,alpha=alpha,ls=ls)

def _weighted_line(ax,q,weight,color=TEAL,lw=1.7,alpha=1,valid=None):
    p=project(q);seg=np.stack([p[:-1],p[1:]],axis=1)
    weight=np.broadcast_to(np.asarray(weight),len(q));value=(weight[:-1]+weight[1:])/2
    keep=np.ones(len(value),bool) if valid is None else valid[:-1]&valid[1:]
    cols=np.tile(to_rgba(color),(len(value),1));cols[:,3]=np.clip(alpha*value,0,1)
    ax.add_collection(LineCollection(seg[keep],colors=cols[keep],linewidths=lw,capstyle='butt'))

def _rod(ax,beta=0,U=np.eye(3),alpha=1,lw=3):
    q=np.c_[np.full(len(LGRID),R*np.cos(beta)),np.full(len(LGRID),R*np.sin(beta)),LGRID]@U.T
    _weighted_line(ax,q,contrast(rod_intensity(LGRID)),lw=lw,alpha=alpha)

def _cylinder(ax,sweep=1,U=np.eye(3),alpha=1,sparse=False):
    if sweep<=1e-5:_rod(ax,U=U,alpha=alpha);return
    beta=np.linspace(0,2*np.pi*sweep,max(4,int(121*sweep)))
    levels=np.linspace(LMIN,LMAX,53 if sparse else 157)
    for L in levels:
        q=np.c_[R*np.cos(beta),R*np.sin(beta),np.full(len(beta),L)]@U.T
        _line(ax,q,alpha=alpha*.56*float(contrast(rod_intensity(L))),lw=.75)
    # Light generatrices establish a hollow surface, not a solid cylinder.
    for b in [0,2*np.pi*sweep]:
        _line(ax,np.array([[R*np.cos(b),R*np.sin(b),LMIN],[R*np.cos(b),R*np.sin(b),LMAX]])@U.T,
              color=GREY,lw=.55,alpha=.5*alpha)
    if sweep<.999:_rod(ax,beta=2*np.pi*sweep,U=U,alpha=alpha,lw=2.8)

def _mosaic(ax,progress=1,alpha=1):
    # Explicit representative cylinder surfaces. The selected Ewald population
    # below uses the complete positive solid-angle quadrature, not these examples.
    if progress<1:_cylinder(ax,alpha=(1-progress)*alpha)
    _cylinder(ax,alpha=.34*alpha*progress,sparse=True)
    for a,b,opacity in [(4,25,.39),(4,145,.39),(4,265,.39),(12,75,.16),(12,195,.16),(12,315,.16)]:
        U=rotation(np.deg2rad(a)*progress,np.deg2rad(b))
        _cylinder(ax,U=U,alpha=opacity*alpha*progress,sparse=True)
        # Two side edges expose the coherent tilt of each surface.
        for az in [np.pi*.25,np.pi*1.25]:
            edge=np.array([[R*np.cos(az),R*np.sin(az),LMIN],[R*np.cos(az),R*np.sin(az),LMAX]])@U.T
            _line(ax,edge,color=GREY,lw=.65,alpha=opacity*alpha*progress)
    for a,b in [(4,25),(4,145),(4,265),(12,75),(12,195),(12,315)]:
        n=rotation(np.deg2rad(a)*progress,np.deg2rad(b))[:,2]
        _arrow(ax,project([0,0,0]),project(.92*n),GREY,.8,5,alpha)

def _sphere(ax,alpha=1):
    p=project(CENTER)
    ax.add_patch(Circle(p,K,facecolor=(.94,.97,.985,.60*alpha),edgecolor=BLUE,lw=.8,alpha=alpha,zorder=-3))
    t=np.linspace(0,2*np.pi,161)
    for a in [0,np.pi/3,2*np.pi/3]:
        q=CENTER+np.c_[K*np.cos(a)*np.cos(t),K*np.sin(a)*np.cos(t),K*np.sin(t)]
        _line(ax,q,color=BLUE,lw=.55,alpha=.22*alpha)

def draw_stage(ax,stage,progress=1.0,*,annotations=True,fontsize=9,compact=False,ideal_reference=False):
    ax.clear();ax.set_xlim(VIEW[:2]);ax.set_ylim(VIEW[2:]);ax.set_aspect('equal');ax.axis('off')
    p=float(np.clip(progress,0,1));stage=int(stage)
    if stage not in range(4):raise ValueError('stage must be 0,1,2,3')
    origin=project([0,0,0]);top=project([0,0,4.15])
    _arrow(ax,origin,top,GREY,.8,6)
    ax.text(*(top+[.13,.10]),r'$Q_z$',fontsize=fontsize)
    ax.scatter(*origin,s=12,color=INK,zorder=8)
    ax.text(*(origin+[.14,-.26]),'O',fontsize=fontsize-1)
    if stage==0:
        layers=opening_layer_count(p)
        if layers==N:
            _rod(ax)  # Exact existing N8 endpoint and downstream intensity.
        else:
            grid,profile=opening_profile_data(layers)
            q=np.c_[np.full(len(grid),R),np.zeros(len(grid)),grid]
            _weighted_line(ax,q,contrast(profile),lw=3)
        if not ideal_reference:
            # Locator symbols expose Bragg maxima when their actual rod widths
            # are subpixel. They are not an additional intensity contribution.
            locator_alpha=float(np.clip(1-64/layers,0,1))
            if locator_alpha>0:
                maxima=project(np.c_[np.full(3,R),np.zeros(3),[1.,2.,3.]])
                ax.scatter(maxima[:,0],maxima[:,1],s=11,color=TEAL,
                    alpha=locator_alpha,linewidths=0,zorder=9)
        for L in [1,2,3]:
            q=project([R,0,L]);ax.text(*(q+[.17,.0]),f'$L={L}$',color=TEAL,fontsize=fontsize)
        ax.text(*project([1.45,0,.06]),r'$r=1$',color=TEAL,fontsize=fontsize)
        # Draw the profile with ordinary axes coordinates, so importers need no
        # additional inset Axes and clearing draw_stage clears all prior content.
        if layers==N:
            l=np.linspace(LMIN,LMAX,800);s=rod_intensity(l)
        else:l,s=opening_profile_data(layers)
        x0,width=(-2.88,1.34) if compact else (-5.0,2.85)
        x1=x0+width
        xp=x0+width*s;yp=project(np.c_[np.full(len(l),R),np.zeros(len(l)),l])[:,1]
        ax.plot(xp,yp,color=INK,lw=1.)
        if ideal_reference:
            for L in [1,2,3]:
                yy=project([R,0,L])[1]
                # The arrow length is symbolic, not a finite peak amplitude.
                _arrow(ax,[x0,yy],[x1+.11*width,yy],GREY,.75,5.7,.95)
        for L in [1,2,3]:
            yy=project([R,0,L])[1]
            ax.plot([x1+.03,.60],[yy,yy],color=GREY,lw=.4,alpha=.4,ls=(0,(2,4)))
        ax.plot([x0,x0],[yp[0],yp[-1]],color=GREY,lw=.6)
        ax.plot([x0,x1],[yp[0],yp[0]],color=GREY,lw=.6)
        profile_label=r'$S_N(L)$' if ideal_reference else r'$S(L;\overline{N})$'
        ax.text(x0+width/2,-.60,profile_label,ha='center',fontsize=fontsize)
        ax.text(x0-.22,3.4,r'$L$',fontsize=fontsize)
        ax.text(x0,-.32,'0',ha='center',fontsize=fontsize-2)
        ax.text(x1,-.32,'1',ha='center',fontsize=fontsize-2)
        if ideal_reference:
            ax.text(x0,4.11,r'Ideal: $\delta$ peaks',color=GREY,fontsize=fontsize-1)
            ax.text(x0,3.72,r'Finite: $N=8$',color=INK,fontsize=fontsize-1)
        else:
            ax.text(x0+width/2,3.60,r'$\overline{N}\approx '+f'{layers:.1f}'+r'$ layers',
                    ha='center',fontsize=fontsize)
        if annotations:ax.text(-5,4.25,'Finite thickness broadens peaks',fontsize=fontsize+1)
    elif stage==1:
        _cylinder(ax,sweep=p)
        _rod(ax,alpha=.32,lw=1.1)
        if annotations:ax.text(-5.15,4.28,'Random in-plane azimuth',fontsize=fontsize+1)
        ax.text(1.26,2.0,r'$r=1$',color=TEAL,fontsize=fontsize)
        label_xy=(-2.51,4.13) if compact else (-4.90,1.63)
        ax.text(*label_xy,r'$\beta:0\rightarrow2\pi$',fontsize=fontsize+1)
        if annotations:ax.text(-4.9,.98,'Same intensity\nalong every rotated rod',fontsize=fontsize,linespacing=1.4)
    elif stage==2:
        _mosaic(ax,p)
        if annotations:ax.text(-5.15,4.28,'Rigidly rotated cylinder surfaces',fontsize=fontsize+1)
        ax.text(1.38,2.0,r'$r=1$',color=TEAL,fontsize=fontsize)
        if annotations:ax.text(-5.10,1.67,'Narrow core\n+ broad angular component',fontsize=fontsize,linespacing=1.4)
    else:
        # First half reveals the sphere while fading representative cylinders.
        sphere_alpha=min(1,p/.48)
        source_alpha=max(0,1-p/.66)
        _sphere(ax,sphere_alpha)
        if source_alpha>0:_mosaic(ax,1,source_alpha)
        selected_alpha=np.clip((p-.40)/.52,0,1)
        structural=rod_intensity(LGRID)
        for loci,mass in selected_population():
            for q,valid in loci:
                # Linear orientation masses weight a fixed contrast of S(L).
                # This qualitative locus drawing is not an Ewald-area or
                # detector count density and does not include coarea weights.
                value=contrast(structural)*mass*9.0
                _weighted_line(ax,q,value,color=TEAL,lw=1.15,alpha=selected_alpha,valid=valid)
        # This dashed line is the exact geometric zero-mosaic locus. Its faint
        # fixed stroke is a reference guide, not added structural intensity.
        for q,valid in exact_locus(np.eye(3)):
            qp=q.copy();qp[~valid]=np.nan
            _line(ax,qp,color=INK,lw=.72,ls=(0,(2.5,2.5)),alpha=.58*sphere_alpha)
        if sphere_alpha>0:
            ax.plot([-5.16,-4.61],[3.74,3.74],color=INK,lw=.85,ls=(0,(2.5,2.5)),alpha=sphere_alpha)
            ax.text(-4.46,3.74,'Aligned',fontsize=fontsize,va='center',alpha=sphere_alpha)
        if selected_alpha>0:
            ax.plot([-5.16,-4.61],[3.30,3.30],color=TEAL,lw=2.1,alpha=selected_alpha)
            ax.text(-4.46,3.30,'Mosaic',fontsize=fontsize,va='center',alpha=selected_alpha)
        c=project(CENTER);_arrow(ax,c,origin,BLUE,1.1,6,sphere_alpha)
        ax.scatter(*c,s=12,color=BLUE,alpha=sphere_alpha)
        ax.text(*(c+[-1.34,-.40]),r'$-\mathbf{k}_i$',color=BLUE,fontsize=fontsize,alpha=sphere_alpha)
        if annotations:ax.text(-5.15,4.78,'Ewald-selected structural intensity',fontsize=fontsize+1,alpha=sphere_alpha)
        # Pick one exact geometric event to identify the outgoing direction.
        q,valid=exact_locus(np.eye(3),np.array([2.]))[0]
        point=project(q[0]);_arrow(ax,c,point,AMBER,1.5,7,selected_alpha)
        ax.scatter(*point,s=22,color=AMBER,edgecolor='white',lw=.6,alpha=selected_alpha,zorder=12)
        ax.text(*((c+point)/2+[-.22,.22]),r'$\mathbf{k}_f$',color=AMBER,fontsize=fontsize+1,alpha=selected_alpha)
        ax.text(-5.1,-1.29,r'$|\mathbf{k}_f|=|\mathbf{k}_i|=2\pi/\lambda$',fontsize=fontsize,alpha=sphere_alpha)
    return ax.get_children()

CAPTION=(
    'From ideal Bragg peaks to finite rods and Ewald-selected scattering. This is a geometric '
    'teaching example, not a material-specific fit. (a) An ideal infinitely repeated crystal '
    'gives zero-width Bragg peaks at integer Bragg order ell, with L the continuous intrinsic '
    'coordinate. Symbolic delta(L-ell) arrows represent these peaks. '
    'The arrows specify positions and zero width, not finite height or integrated weight. '
    'Finite thickness replaces this ideal picture with broadened peaks and fringes. For N '
    'identical unit layers, each finite curve is separately peak normalized as '
    'S_N(L)=|sum from n=0 to N-1 of exp(2 pi i n L)|^2/N^2. The static comparison shows '
    'gray ideal delta arrows and a dark finite N=8 curve. '
    'The accompanying animation instead begins with a narrow but finite 512-layer profile '
    'and broadens continuously to N=8. A continuous mean layer count Nbar=m+f describes '
    'population fractions 1-f of m-layer stacks and f of (m+1)-layer stacks, where m is '
    'the integer floor of Nbar. Their incoherent intensities are mixed and then peak '
    'normalized: S(L;Nbar)=[(1-f)m^2 S_m(L)+f(m+1)^2 S_(m+1)(L)]/D, with '
    'D=(1-f)m^2+f(m+1)^2. The mean is a thickness-population mean, not fractional atomic '
    'layers. Inverse mean thickness increases linearly with rendering progress; the '
    'movie varies that progress quadratically in elapsed opening time. Small teal '
    'markers locate the three Bragg maxima while their rod widths are visually unresolved, '
    'and fade away by Nbar=64; these markers do not add structural intensity. '
    'This peak-normalized sequence is not a conserved-area transformation: each mixture '
    'has unit-period area Nbar/D, reducing to 1/N for a pure integer stack. Only pure '
    'integer stacks have first-zero full width 2/N; neighboring-stack mixtures can fill '
    'each other\'s zeros. The static ideal delta symbols use a separate schematic convention. '
    'A normalized delta-comb limit requires the pure coherent factor divided by N. No stacking faults '
    'are needed to produce these finite-stack fringes. L is the crystallite-frame rod '
    'coordinate, and in-plane periodicity remains ideal. '
    '(b) Uniform, independent in-plane azimuth beta distributes the off-axis rod over a thin '
    'cylinder of radius R=1 in arbitrary reciprocal units. The same S(L) decorates every '
    'azimuth, using the final N=8 profile S_8. The displayed r=1 is a representative basal reflection family, not a Bi2Se3 '
    'or Bi2Te3 allowed-reflection list. (c) Representative rigidly tilted cylinder surfaces '
    'illustrate mosaic orientations. Their intrinsic profiles rotate with the crystallites. '
    'Mosaicity is not a uniform radial blur, and intrinsic L is not laboratory Qz after tilt. '
    '(d) The dashed curve is the exact untilted cylinder/Ewald intersection. Teal loci '
    'show the orientation-weighted selection from the tilted cylinders. Each curve obeys '
    '|ki+Q|=|ki|, with sphere center -ki and radius 2 pi/lambda. The orange radius identifies '
    'one exact aligned exit vector kf. The 12-by-32 positive quadrature samples normal tilt '
    'alpha and its independent azimuth psi using the solid-angle measure. The illustrative '
    'law is an 82% Gaussian core of width 3 degrees and an 18% broader Gaussian of width '
    '9 degrees, each normalized on the retained quadrature within an 18-degree cone. '
    'The profile plot is linear. Structural-color contrast is fixed at asinh(S/0.02)/asinh(50), '
    'and each selected curve receives its linear orientation weight after this contrast. '
    'Light cylinder edges and the dashed aligned curve are geometric guides. Qz is a reference '
    'axis, not an added specular rod. Panels a-c share an enlarged scale, while d zooms out '
    'without changing viewpoint. These are qualitative weighted loci, not Ewald-area or '
    'detector-count densities. Structure factors, coarea and detector Jacobians, optical '
    'response, beam spread and opaque-substrate acceptance are not included. Stacking faults '
    'would change S(L) on the existing rods, while retaining this orientation and selection framework.'
)

def export_data_and_provenance():
    """Write portable direct arrays and a numerical/model/display record only."""
    (OUT/'data').mkdir(parents=True,exist_ok=True)
    (OUT/'provenance').mkdir(exist_ok=True)
    states=np.array(orientation_states());qall=[];validall=[]
    max_ewald=0.;max_L=0.;max_radius=0.;max_rotation=0.
    for alpha,psi,mass in states:
        U=rotation(alpha,psi);n=U[:,2]
        max_rotation=max(max_rotation,float(np.max(np.abs(U.T@U-np.eye(3)))))
        qs=[];masks=[]
        for q,mask in exact_locus(U):
            selected=q[mask];ell=LGRID[mask]
            max_ewald=max(max_ewald,float(np.max(np.abs(np.linalg.norm(selected+KI,axis=1)-K))))
            max_L=max(max_L,float(np.max(np.abs(selected@n-ell))))
            radial=selected-(selected@n)[:,None]*n
            max_radius=max(max_radius,float(np.max(np.abs(np.linalg.norm(radial,axis=1)-R))))
            stored=q.copy();stored[~mask]=np.nan
            qs.append(stored);masks.append(mask)
        qall.append(qs);validall.append(masks)
    qall=np.array(qall);validall=np.array(validall)
    profile=rod_intensity(LGRID)
    path=OUT/'data/model_arrays.npz'
    np.savez_compressed(path,L=LGRID,S=profile,alpha_rad=states[:,0],psi_rad=states[:,1],
        orientation_mass=states[:,2],q=qall,valid=validall,ki=KI,K=np.array(K),R=np.array(R))
    np.savetxt(OUT/'data/rod_profile.csv',np.c_[LGRID,profile],delimiter=',',
        header='intrinsic_L,S_normalized_to_ordered_peak',comments='',fmt='%.17g')
    np.savetxt(OUT/'data/orientation_quadrature.csv',np.c_[np.rad2deg(states[:,:2]),states[:,2]],
        delimiter=',',header='normal_tilt_alpha_deg,normal_azimuth_psi_deg,orientation_mass',
        comments='',fmt='%.17g')
    # Representative direct profiles; the portable helper evaluates any mean.
    means=np.array([512.,128.,32.,16.,8.5,8.])
    lower=np.floor(means).astype(int);fractions=means-lower
    opening_L=np.unique(np.concatenate([opening_profile_data(n)[0] for n in means]))
    opening_S=np.array([thickness_population_profile(opening_L,n) for n in means])
    opening_path=OUT/'data/opening_profiles.npz'
    np.savez_compressed(opening_path,L=opening_L,mean_layers=means,
        lower_integer_layers=lower,upper_integer_fraction=fractions,S_peak_normalized=opening_S)
    period_grid=np.arange(32768)/32768
    normalization=[]
    for mean,m,f in zip(means,lower,fractions):
        denominator=(1-f)*m*m+f*(m+1)*(m+1)
        profile_n=thickness_population_profile(period_grid,mean)
        normalization.append([mean,m,f,denominator,float(profile_n.mean()),mean/denominator,
            2/mean if f==0 else np.nan])
    np.savetxt(OUT/'data/opening_normalization.csv',np.array(normalization),delimiter=',',
        header='mean_layers,lower_integer_layers,upper_integer_fraction,mixed_peak_denominator,numerical_period_mean,expected_period_mean,first_zero_full_width_if_pure_integer',
        comments='',fmt='%.17g')
    (OUT/'caption.txt').write_text(CAPTION+'\n',encoding='utf-8')
    checks={'pass':True,'retained_orientations':len(states),
        'valid_selected_points':int(validall.sum()),'max_ewald_radius_residual':max_ewald,
        'max_intrinsic_L_error':max_L,'max_cylinder_radius_error':max_radius,
        'max_rotation_orthogonality_error':max_rotation,
        'orientation_mass_sum':float(states[:,2].sum()),'minimum_orientation_mass':float(states[:,2].min()),
        'ordered_peak_values':rod_intensity(np.arange(5)).tolist(),
        'period_mean':float(rod_intensity(np.arange(4096)/4096).mean()),'expected_period_mean':1/N}
    checks['pass']=bool(max_ewald<1e-12 and max_L<1e-12 and max_radius<1e-12
        and abs(checks['orientation_mass_sum']-1)<1e-12
        and abs(checks['period_mean']-1/N)<1e-12 and states[:,2].min()>0)
    if not checks['pass']:raise AssertionError(checks)
    sh=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    checks['opening_max_period_mean_error']=float(max(abs(row[4]-row[5]) for row in normalization))
    checks['opening_N8_matches_existing_profile']=bool(np.array_equal(thickness_population_profile(LGRID,8),rod_intensity(LGRID)))
    checks['opening_mean_layers']={'initial_finite':opening_layer_count(0),'final':opening_layer_count(1)}
    grid512,profile512=opening_profile_data(512.)
    checks['opening_N512_half_height_samples_at_L1']=int(np.sum((np.abs(grid512-1)<1/512)&(profile512>=.5)))
    checks['opening_archived_minimum_intensity']=float(opening_S.min())
    checks['opening_max_integer_peak_error']=float(max(np.max(np.abs(thickness_population_profile(np.arange(1.,4.),n)-1)) for n in means))
    assert checks['opening_max_period_mean_error']<1e-12 and checks['opening_N8_matches_existing_profile']
    assert checks['opening_N512_half_height_samples_at_L1']>=30 and checks['opening_archived_minimum_intensity']>=0
    record={'schema':'cylinder-bridge-v3','title':'From narrow finite peaks to rods and Ewald-selected scattering',
        'science_status':'generic finite ordered stack and qualitative geometric selection, not a fitted result',
        'source':'source/cylinder_bridge.py','source_sha256':sh(Path(__file__)),
        'portable_rebuild':'python source/cylinder_bridge.py','libraries':['numpy','matplotlib'],
        'opening':{'initial_state':'finite512-layer profile; same plotted curve geometry throughout the animation',
            'static_ideal_reference':'unchanged symbolic gray delta arrows beside final N8 curve; no finite arrow height/weight interpretation',
            'representative_mean_layers':means.tolist(),
            'population_model':'mean=m+f; fractions1-f of integer m-layer stacks and f of integer(m+1)-layer stacks; incoherent intensity mixture, not fractional atomic layers',
            'integer_profile':'S_N(L)=|sum(exp(2*pi*i*n*L),n=0..N-1)|^2/N^2',
            'normalization':'S(L;mean)=[(1-f)*m^2*S_m+f*(m+1)^2*S_(m+1)]/D; D=(1-f)*m^2+f*(m+1)^2; peaks1; unit-period area mean/D',
            'no_conserved_area_claim':True,'delta_comb_normalization_for_comparison':'|sum|^2/N rather than the plotted |sum|^2/N^2',
            'progress_to_mean_layers':'1/(1/512+(1/8-1/512)*clip(p,0,1))',
            'movie_progress_reference':'p=u^2 during the opening broadening interval; final timing owned by animation source/manifest',
            'opening_only_dense_grid':'32769 regular samples plus exact integer orders, neighboring-stack first zeros, and801 peak-local nodes per Bragg order over+/-6/mean',
            'archive_grid':'union of representative opening grids; arbitrary means recreated from the portable source',
            'integer_first_zero_width':'2/N only for pure integer stacks; neighboring thickness mixtures generally fill each other\'s zeros',
            'original_N8_endpoint':'original rod grid and profile renderer retained at stage0,N8',
            'data':'data/opening_profiles.npz','data_sha256':sh(opening_path),
            'normalization_csv':'data/opening_normalization.csv'},
        'parameters':{'N':N,'R':R,'K':K,'incidence_degrees':INCIDENCE_DEG,'intrinsic_L_range':[LMIN,LMAX],
            'core_sigma_degrees':SIGMA_CORE_DEG,'broad_sigma_degrees':SIGMA_BROAD_DEG,
            'broad_probability':BROAD_FRACTION,'maximum_tilt_degrees':MAX_TILT_DEG,
            'normal_quadrature':[N_ALPHA,N_AZIMUTH],
            'orientation_measure':'positive polar Gauss-Legendre with sin(alpha) d(alpha), uniform independent normal azimuth psi; components normalized on retained nodes',
            'powder_azimuth':'independent beta, analytically solved on each rigidly rotated cylinder',
            'view_yaw_degrees':-45,'view_elevation_degrees':20},
        'display':{'structural_contrast':'C(S)=asinh(S/0.02)/asinh(50)',
            'opening_bragg_locators':'animation stage0 only; teal symbols s=11 at intrinsic L1,2,3; alpha=clip(1-64/mean,0,1); position guides for unresolved maxima, not additional intensity',
            'selected_locus_opacity':'9 * orientation_mass * C(S); scene fade multiplies opacity',
            'selected_locus_stroke_points':1.15,'coarea_or_detector_density':False,
            'representative_cylinders':'mean plus six surfaces at illustrative 4/12 degree tilts; geometry guides, not the numerical normal quadrature',
            'static_framing':'a-c same enlarged limits, d expands to whole sphere; camera fixed',
            'missing_rods':'no r=0 response is drawn; Qz line is a coordinate axis'},
        'data':{'npz':'data/model_arrays.npz','npz_sha256':sh(path),
            'csv':['data/rod_profile.csv','data/orientation_quadrature.csv'],
            'q_dimensions':['orientation','analytic_beta_branch','intrinsic_L_sample','xyz'],
            'invalid_points':'q is NaN where valid is false; these are not selected scattering points'},
        'checks':checks,'caption_file':'caption.txt','caption':CAPTION}
    (OUT/'provenance/Cylinder_Bridge.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return checks

def main():
    setup();OUT.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(7.2,5.45))
    titles=['Finite thickness broadens peaks','Azimuth creates the cylinder','Mosaic tilts the cylinders','Ewald selects the scattering']
    for j,ax in enumerate(axes.flat):
        draw_stage(ax,j,annotations=False,fontsize=8.5,compact=True,ideal_reference=(j==0))
        if j<3:
            ax.set_xlim(-3.15,2.25);ax.set_ylim(-.90,4.60)
        ax.set_title(f'{chr(97+j)}  {titles[j]}',loc='left',fontsize=10,pad=8)
    fig.subplots_adjust(left=.035,right=.985,top=.94,bottom=.07,wspace=.13,hspace=.17)
    fig.text(.5,.024,'Geometric teaching example. Next: stacking changes intensity along the rods.',
        ha='center',fontsize=8,color=INK)
    for ext in ['png','svg','pdf']:fig.savefig(OUT/f'Cylinder_Bridge.{ext}',dpi=320,bbox_inches='tight',pad_inches=.08)
    export_data_and_provenance()
    print(OUT/'Cylinder_Bridge.png')

if __name__=='__main__':main()
