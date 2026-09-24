"""Analytic teaching figures for the SI; no experimental or fitted inputs."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '2D_Supplemental/figures'
QA = ROOT / 'output/si_reorganization'
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
plt.style.use(ROOT / 'scripts/si-figures.mplstyle')
# 8.5-inch SI page minus two 1.1-inch margins; no reduction on insertion.
WIDTH_IN = 6.3
purple, amber, teal = '#79529D', '#C17A24', '#087D88'
checks = {}

def export(fig, name):
    fig.canvas.draw()
    bounds = fig.bbox
    outside = []
    for text in fig.findobj(matplotlib.text.Text):
        if text.get_visible() and text.get_text():
            b = text.get_window_extent(fig.canvas.get_renderer())
            if b.width > 0 and (b.x0 < bounds.x0-1 or b.y0 < bounds.y0-1 or b.x1 > bounds.x1+1 or b.y1 > bounds.y1+1):
                outside.append(text.get_text())
    assert not outside, outside
    for suffix in ('pdf','svg','png'):
        fig.savefig(OUT / f'{name}.{suffix}', dpi=600, facecolor='white')
    checks[name] = {'all_text_within_canvas':True, 'size_inches':list(fig.get_size_inches()),
                   'final_width_inches':WIDTH_IN, 'minimum_base_font_pt':8.5,
                   'minimum_line_width_pt':0.5, 'png_dpi':600}
    plt.close(fig)

# The angle density is normalized on the full periodic domain, before cropping.
sigma, gamma, tail = np.deg2rad(1), np.deg2rad(2), .2
def gaussian(a):
    return sum(np.exp(-.5*((np.asarray(a)+2*np.pi*q)/sigma)**2)/(np.sqrt(2*np.pi)*sigma) for q in range(-2,3))
def lorentzian(a):
    return np.sinh(gamma)/(2*np.pi*(np.cosh(gamma)-np.cos(a)))
rad_per_degree = np.pi/180
signed_x = np.linspace(-12,12,2401)
folded_x = np.linspace(0,12,1201)
def curves(x, fold):
    g = fold*(1-tail)*gaussian(np.deg2rad(x))*rad_per_degree
    l = fold*tail*lorentzian(np.deg2rad(x))*rad_per_degree
    return g, l, g+l
fig, axes = plt.subplots(1,3,figsize=(WIDTH_IN,2.6))
fig.subplots_adjust(left=.09,right=.975,bottom=.23,top=.76,wspace=.51)
for i,(ax,x,fold) in enumerate(zip(axes,[signed_x,folded_x,folded_x],[1,2,2])):
    for y,color,label,style in zip(curves(x,fold),[purple,amber,'#202020'],
                                 ['Weighted Gaussian','Weighted Lorentzian','Sum'],['--','-.','-']):
        ax.plot(x,y,color=color,lw=1.1,ls=style,label=label)
    ax.set_title(f'({chr(97+i)})',loc='left',pad=7,fontweight='bold')
    ax.set_xlabel(r'$\Delta\theta$ (deg)' if i==0 else r'$\alpha$ (deg)')
    ax.set_xlim(x[0],x[-1])
    ax.set_xticks([-10,0,10] if i==0 else [0,4,8,12])
    ax.spines[['top','right']].set_visible(False)
    if i<2:
        ax.set_ylim(0,.8)
        ax.set_yticks([0,.2,.4,.6,.8])
    else:
        ax.set_yscale('log'); ax.set_ylim(1e-5,1)
        ax.set_yticks([1e-5,1e-3,1e-1,1])
axes[0].set_ylabel(r'Density (deg$^{-1}$)')
axes[2].set_ylabel(r'Density (deg$^{-1}$)')
fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,1),ncol=3)
export(fig,'mosaic_measure_guide')
mass_g = 2*quad(gaussian,0,np.pi,epsabs=1e-11)[0]
mass_l = 2*quad(lorentzian,0,np.pi,epsabs=1e-11)[0]
assert abs(mass_g-1)<1e-10 and abs(mass_l-1)<1e-10
checks['mosaic_probabilities']={'gaussian_mass':mass_g,'lorentzian_mass':mass_l,
                              'mixture_mass':(1-tail)*mass_g+tail*mass_l,
                              'parameters_are_illustrative':True,
                              'sigma_deg':1,'gamma_deg':2,'tail_weight':tail}
np.savez(QA/'mosaic_guide_analytic_curves.npz',signed_angle_deg=signed_x,
         signed_curves=np.array(curves(signed_x,1)),folded_angle_deg=folded_x,
         folded_curves=np.array(curves(folded_x,2)))

# Geometric band mapping: v=y-f(x), projected drawing coordinate=x. No synthetic intensity is used.
fig = plt.figure(figsize=(WIDTH_IN,2.35))
ax = fig.add_axes([.085,.24,.23,.57])
bx = fig.add_axes([.405,.24,.23,.57])
cx = fig.add_axes([.71,.24,.28,.57]); cx.axis('off')
x=np.linspace(0,6,500)
center = .09*(x-3)**2+2
half=.42
ax.fill_between(x,center-half,center+half,color=teal,alpha=.22)
select=(x>=2)&(x<=3)
ax.fill_between(x,center-half,center+half,where=select,color=teal,alpha=.6)
ax.plot(x,center,'--',color=teal,lw=1)
for value in np.arange(0,6.01,.5):
    ax.axvline(value,color='#c5c5c5',lw=.5,zorder=0)
    ax.axhline(value,color='#c5c5c5',lw=.5,zorder=0)
ax.set(xlim=(0,6),ylim=(0,5),xlabel='Detector column',ylabel='Detector row')
ax.set_xticks([]);ax.set_yticks([])
ax.set_title('(a)',loc='left',pad=7,fontweight='bold')
bx.add_patch(Rectangle((0,-half),6,2*half,facecolor=teal,alpha=.22,edgecolor='none'))
bx.add_patch(Rectangle((2,-half),1,2*half,facecolor=teal,alpha=.6,edgecolor='none'))
for value in np.arange(0,6.01,.5): bx.axvline(value,color='#c5c5c5',lw=.5,zorder=0)
for value in np.arange(-1,1.01,.2): bx.axhline(value,color='#c5c5c5',lw=.5,zorder=0)
bx.axhline(0,color=teal,ls='--',lw=1)
bx.set(xlim=(0,6),ylim=(-1,1),xlabel=r'Projected coordinate $L_{\rm proj}$',ylabel='Transverse offset')
bx.set_xticks([]);bx.set_yticks([])
bx.set_title('(b)',loc='left',pad=7,fontweight='bold')
for plot in (ax,bx): plot.spines[['top','right']].set_visible(False)
fig.add_artist(FancyArrowPatch((.323,.53),(.368,.53),transform=fig.transFigure,arrowstyle='-|>',mutation_scale=10,color='#555555',lw=.9))
cx.set_title('(c)',loc='left',pad=7,fontweight='bold')
cx.text(.01,.77,r'$S_\nu=\sum_p a_{\nu p}s_p$',fontsize=10)
cx.text(.01,.43,r'$N_\nu=\sum_p a_{\nu p}n_p$',fontsize=10)
cx.text(.01,.09,r'$I_\nu^{\rm ROI}=S_\nu/N_\nu$',fontsize=10)
export(fig,'profile_construction_guide')
checks['profile_guide']={'schematic_only':True,'contains_intensity_data':False,
                         'mapping':'projected_coordinate=x; transverse=y-(0.09*(x-3)^2+2)',
                         'band_half_width':half,'selected_interval':[2,3],
                         'coordinate_units':'arbitrary drawing units'}
(QA/'guide_verification.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks,indent=2))
