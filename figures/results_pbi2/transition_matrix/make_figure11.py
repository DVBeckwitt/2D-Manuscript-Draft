"""Draw Figure 11 from the retained, SI-verified atomic-coordinate export.

Run from any directory: python figures/results_pbi2/transition_matrix/make_figure11.py
The source export is preserved byte-for-byte; all dimensions here are schematic.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'output/manuscript_figure_drafts_v1/data/stacking/F07_atomic_geometry.json'
OUT = ROOT / 'output/figure11_redesign'
OUT.mkdir(parents=True, exist_ok=True)
g = json.loads(SOURCE.read_text(encoding='utf-8'))
INK, ACCENT = '#151515', '#087D88'
COLORS = g['atom_colors']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'text.color': INK, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})

# Check the displayed states against the SI definitions and retained parent matrices.
expected = {'2H': [0]*6, '4H': [0,4]*3, '6H': [0,1,2]*2}
for name, seq in expected.items():
    parent = g['parents'][name]
    assert parent['sequence'] == seq
    for a, b in zip(seq, seq[1:]+[0]):
        assert parent['matrix'][a][b] == 1
for state in g['states']:
    assert state['registry'] == state['index'] % 3
    assert len(state['atoms']) == 8
    for atom in state['atoms']:
        top = (atom['plane'] == 'top') == (state['index'] < 3)
        local = [0,0] if atom['element'] == 'Pb' else ([2/3,1/3] if top else [1/3,2/3])
        assert atom['localFractional'] == local
        assert atom['registryFractional'] == g['registries'][state['registry']]
        assert math.isclose(atom['x'], atom['basalFractional'][0], abs_tol=1e-14)
    assert all(math.isclose(b['basalDistanceSquared'], 1/3, abs_tol=1e-14) for b in state['bonds'])

fig, ax = plt.subplots(figsize=(7.2,7.2*35.7/90.5))
fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
ax.set(xlim=(-.5,90), ylim=(3.8,39.5), aspect='equal')
ax.axis('off')

def text(x,y,s,size=8,**kw):
    return ax.text(x,y,s,fontsize=size,va='center',**kw)

def label(s):
    return rf'${s%3}F_{{{"+" if s<3 else "-"}}}$'

def layer(state, x, y, scale=6.0):
    geom = g['states'][state]
    for bond in geom['bonds']:
        (a,b),(c,d) = bond['fromXY'], bond['toXY']
        mx,my=(a+c)/2,(b+d)/2
        ax.plot([x+scale*a,x+scale*mx],[y-scale*b,y-scale*my],color=COLORS['Pb'],lw=.95,zorder=2)
        ax.plot([x+scale*mx,x+scale*c],[y-scale*my,y-scale*d],color=COLORS['I'],lw=.95,zorder=2)
    for atom in geom['atoms']:
        size = 32 if atom['element']=='Pb' else 19
        ax.scatter(x+scale*atom['x'],y-scale*atom['y'],s=size,c=COLORS[atom['element']],
                   edgecolors='white',linewidths=.35,zorder=4)

for x,element in [(14,'Pb'),(23,'I')]:
    ax.scatter(x,36.8,s=32 if element=='Pb' else 19,color=COLORS[element])
    text(x+2.0,36.8,element,8.5)

# One shared legend row. Registry coordinates are defined in the caption.
text(38,36.8,r'$F_+$',9,ha='right')
layer(0,44,36.8,4.7)
text(62,36.8,r'$F_-$',9,ha='right')
layer(3,68,36.8,4.7)

spacing=4.6
origins=[9.5,38.5,67.5]
for col,(name,seq) in enumerate(expected.items()):
    x=origins[col]
    center=x+7
    text(x-7.5,33,f'({chr(97+col)})',9,weight='bold')
    text(center,33,name,10,ha='center',weight='bold')
    # Connect the same Pb site to reveal the registry sequence.
    ys=[6.8+n*spacing for n in range(6)]
    xs=[x+6*g['registries'][s%3][0] for s in seq]
    ax.plot(xs,ys,color=ACCENT,lw=.85,ls=(0,(2,2)),zorder=0)
    # Label the first bottom-to-top interface, matching the manuscript law.
    event = {'2H':r'$a$', '4H':r'$d_+$', '6H':r'$b_+$'}[name]
    text((xs[0]+xs[1])/2+2.2,(ys[0]+ys[1])/2,event,8.4,
         ha='left',color=ACCENT)
    for y,s in zip(ys,seq):
        layer(s,x,y)
        text(x-5.6,y,label(s),8.4,ha='center')
    period=len(g['parents'][name]['cycle'])
    lo,hi=5,6.8+(period-1)*spacing+1.8
    bx=x+17.8
    ax.plot([bx-1,bx,bx,bx-1],[lo,lo,hi,hi],color=ACCENT,lw=1)
    text(bx+1.55,(lo+hi)/2,'1 repeat',7.1,rotation=90,ha='center',color=ACCENT)

ax.annotate('',xy=(.8,28.4),xytext=(.8,21),arrowprops={'arrowstyle':'-|>','color':INK,'lw':.8})
text(.8,29.8,r'$c$',8.5,ha='center')

stem='Figure_11_PbI2_parent_stacking'
for ext in ['png','pdf','svg']:
    fig.savefig(OUT/f'{stem}.{ext}',dpi=320,facecolor='white')
shutil.copyfile(OUT/f'{stem}.pdf',HERE/'pbi2_parent_stacking_redesigned.pdf')
shutil.copyfile(SOURCE,OUT/'atomic_geometry.json')
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'verification.json').write_text(json.dumps({
    'source': str(SOURCE.relative_to(ROOT)), 'source_sha256':sha(SOURCE),
    'generator_sha256':sha(Path(__file__)), 'sequences_bottom_to_top':expected,
    'labeled_interface_events':{'2H':'a: 0F+ -> 0F+', '4H':'d+: 0F+ -> 1F-',
                                '6H':'b+: 0F+ -> 1F+'},
    'checks': ['All six SI registry and iodine orientation definitions',
               'All displayed parent transitions including cycle closure',
               '48 atomic coordinates and all nearest-neighbor projected bonds',
               'Six trilayers per column, equal drawing scale, repeat lengths 1/2/3'],
    'scope':'Ideal parent schematic, nonmetric projection. No fitted populations or measured intensities.',
    'outputs':{e:sha(OUT/f'{stem}.{e}') for e in ['png','pdf','svg']}
},indent=2)+'\n',encoding='utf-8')
print(OUT/f'{stem}.png')
