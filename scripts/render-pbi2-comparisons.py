"""Redraw archived PbI2 and Bi2X3 profiles with compact shared axes.

First run: --archive PATH freezes the compact plotting inputs in output/pbi2_compact.
Later runs use only those local inputs and the retained presentation detector PNGs.
No fit, smoothing, intensity reconstruction, or new uncertainty calculation is run.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
from unittest.mock import patch

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pbi2_compact'
INPUT = OUT / 'source'
ASSETS = ROOT / 'figures/results_pbi2/presentation_v10_cases'
NAMES = ('m1_minus', 'm1_plus', 'm3_minus', 'm3_plus', 'm4_minus', 'm4_plus', 'm0')
STEMS = {'gd1': 'a_2h', 'sid1': 'b_2h_strong_mosaic', 'b4': 'c_2h_6h', 'clean1': 'd_2h_6h_4h'}
STEMS.update({'bi2se3': 'bi2se3', 'bi2te3': 'bi2te3'})
COLORS = {'2H': '#347ba1', '4H': '#8759a5', '6H': '#188777',
          'Bi₂Se₃': '#347ba1', 'Bi₂Te₃': '#347ba1'}
WIDTH, HEIGHT = 7.2, 5.35


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_inputs(archive):
    INPUT.mkdir(parents=True, exist_ok=True)
    sources = {kind: archive / name for kind, name in {
        'profiles': 'all_six_full_span_20260911.ra_diag.npz',
        'uncertainty': 'all_six_full_span_uncertainty_20260911.ra_diag.npz',
        'targets': 'all_six_illustrative_targets_20260911.ra_diag.npz',
    }.items()}
    manifests = {k: json.loads(p.with_suffix('.json').read_text(encoding='utf-8')) for k, p in sources.items()}
    for kind, source in sources.items():
        assert sha(source) == manifests[kind]['sha256'], source
    assert manifests['uncertainty']['source_pack_sha256'] == sha(sources['profiles'])
    assert manifests['targets']['source_data_sha256'] == sha(sources['profiles'])
    assert manifests['targets']['source_uncertainty_sha256'] == sha(sources['uncertainty'])
    module_path = archive / 'render_full_span_fits_20260911.py'
    spec = importlib.util.spec_from_file_location('archived_profile_renderer', module_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    arrays, samples = {}, {}
    with np.load(sources['profiles']) as source, np.load(sources['uncertainty']) as uncertainty, np.load(sources['targets']) as targets:
        for key in STEMS:
            meta = manifests['profiles']['samples'][key]
            record = next(r for r in manifests['targets']['figures'] if r['sample'] == key)
            area = source[f'{key}__projection__area']
            measured = source[f'{key}__projection__measured']
            background = source[f'{key}__projection__background']
            target = targets[f'{key}__illustrative_target_count_per_px2']
            for name, values in {
                'area': area, 'measured_sum': measured, 'background_sum': background,
                'data': np.divide(measured-background, area, out=np.full_like(area, np.nan), where=area>0),
                'comparison': source[f'{key}__projection__fitted'] & (area>0),
                'sigma': uncertainty[f'{key}__band_halfwidth_count_per_px2'],
                'target': target,
            }.items():
                arrays[f'{key}__{name}'] = values.copy()
            # Recover the archived axis framing without exporting or recomputing targets.
            def catalogue(*args):
                return {r: [] for r in (0, 1, 3, 4)}, record['bragg_guides']['periodic_parent_fractions'], {'cstar_Ainv': meta['cstar_Ainv'], 'reference_wavelength_A': record['bragg_guides']['reference_wavelength_A']}
            with patch.object(renderer, 'bragg_catalogue', catalogue), patch.object(Figure, 'savefig'), patch.object(plt, 'close'):
                renderer.render(key, illustrative_target=target)
                fig = plt.gcf()
                limits = {name: {'x': list(ax.get_xlim()), 'y': list(ax.get_ylim())} for name, ax in zip(NAMES, fig.axes, strict=True)}
            plt.close(fig)
            samples[key] = {'branches': meta['branches'], 'scales': record['y_scales'], 'limits': limits, 'guides': record['bragg_guides'],
                            'original_profile_png_sha256': record['png_sha256']}
    np.savez_compressed(INPUT / 'profiles.npz', **arrays)
    metadata = {'samples': samples, 'sources': {k: {'path': str(p), 'sha256': sha(p)} for k, p in sources.items()},
                'original_renderer_sha256': sha(module_path), 'profiles_sha256': sha(INPUT / 'profiles.npz'),
                'scope': 'Unchanged archived observations, conditional uncertainty, masks and editorial target arrays. Targets are not fits.'}
    (INPUT / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')


def intervals(ax, edges, mask):
    changes = np.flatnonzero(np.diff(np.r_[False, mask, False]))
    for first, last in zip(changes[::2], changes[1::2], strict=True):
        ax.axvspan(edges[first], edges[last], color='#eeeeee', lw=0, zorder=-2)


def opacity(offset):
    edge = np.exp(-.5)
    return .64 * np.clip((np.exp(-.5 * offset**2)-edge)/(1-edge), 0., 1.)


def profile(ax, key, name, data, meta, frame, show_y, show_x, receipt):
    spec = meta['branches'][name]
    sl = slice(spec['start'], spec['stop'])
    edges = np.asarray(spec['edges'])
    x = (edges[:-1]+edges[1:])/2
    mask = data[f'{key}__comparison'][sl]
    y, target, sigma = [data[f'{key}__{v}'][sl] for v in ('data','target','sigma')]
    scale = frame['scale']
    if scale == 'asinh':
        ax.set_yscale('asinh', linear_width=1.)
    else:
        ax.set_yscale('log', nonpositive='mask')
    ax.set_xlim(frame['x'])
    ax.set_ylim(frame['y'])
    intervals(ax, edges, ~mask)
    lo, hi = ax.get_ylim()
    prior_alpha = 0.
    for outer, inner in zip(np.linspace(1,0,49)[:-1], np.linspace(1,0,49)[1:], strict=True):
        alpha = opacity((outer+inner)/2)
        layer = (alpha-prior_alpha)/(1-prior_alpha)
        prior_alpha = alpha
        lower, upper = y-outer*sigma, y+outer*sigma
        visible = mask.copy()
        if scale == 'log':
            visible &= upper > lo
            lower = np.maximum(lower, lo)
        ax.fill_between(x, np.where(visible,lower,np.nan), np.where(visible,upper,np.nan),
                        color='#83909d', alpha=layer, lw=0, zorder=1, rasterized=True)
    for sign in (-1,1):
        boundary = y+sign*sigma
        visible = mask & ((boundary>lo) if scale=='log' else True)
        ax.plot(x,np.where(visible,boundary,np.nan),color='#8c96a1',lw=.35,alpha=.65,zorder=1.5)
    visible_data = mask & ((y>0) if scale=='log' else True)
    visible_target = mask & ((target>0) if scale=='log' else True)
    line, = ax.plot(x,np.where(visible_data,y,np.nan),color='#272e36',marker='.',ms=1.7,lw=.65,zorder=3)
    stairs = ax.stairs(np.where(visible_target,target,np.nan),edges,baseline=None,color='#df6800',ls=(0,(4,2.5)),lw=.9,zorder=4)
    # Verify the artists contain the exact archived numeric values at exact bin locations.
    np.testing.assert_array_equal(line.get_xdata(),x)
    np.testing.assert_array_equal(line.get_ydata(),np.where(visible_data,y,np.nan))
    np.testing.assert_array_equal(stairs.get_data().values,np.where(visible_target,target,np.nan))
    np.testing.assert_array_equal(stairs.get_data().edges,edges)
    for guide in meta['guides']['displayed'][name]:
        count = len(guide['parents'])
        for i, parent in enumerate(guide['parents']):
            fraction = meta['guides']['periodic_parent_fractions'][parent]
            ax.axvline(guide['x'],ymin=.015,ymax=.985,color=COLORS[parent],lw=.5,
                       alpha=.27 if fraction<.0001 else .58,ls=(5*i,(3,5*count-3)),zorder=1.7)
    if scale=='asinh':
        levels = np.array([-1e6,-1e5,-1e4,-1e3,-100,-10,-1,0,1,10,100,1e3,1e4,1e5,1e6])
        ticks = levels[(levels>=lo)&(levels<=hi)]
        # Remove crowded +/-1 labels when the range spans several decades.
        if max(abs(lo),abs(hi))>20:
            ticks = ticks[np.abs(ticks)!=1]
        if len(ticks)>6:
            ticks = ticks[::2]
        ax.yaxis.set_major_locator(FixedLocator(ticks))
        ax.axhline(0,color='#a7afb9',lw=.4,zorder=.5)
    else:
        ticks = 10.**np.arange(-4,8)
        ticks = ticks[(ticks>=lo)&(ticks<=hi)]
        ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p: f'{v:g}' if abs(v)<1000 else (rf'$10^{{{int(np.log10(v))}}}$' if v>0 else rf'$-10^{{{int(np.log10(-v))}}}$')))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xticks(frame['ticks'])
    ax.tick_params(labelleft=show_y,labelbottom=show_x,left=show_y,bottom=show_x,
                   length=2,width=.5,pad=2,labelsize=7)
    ax.set_xlim(frame['x'])
    ax.grid(True,color='#e6eaf0',lw=.4)
    ax.set_ylim(lo,hi)
    if key.startswith('bi2') and name=='m0':
        for guide in meta['guides']['displayed'][name]:
            ax.text(guide['x'],.97,f"00{int(guide['L'])}",transform=ax.get_xaxis_transform(),
                    fontsize=5.5,color='#647487',ha='center',va='top')
    receipt.append({'sample':key,'branch':name,'comparison_bins':int(mask.sum()),'axis_scale':scale,
                    'xlim':list(ax.get_xlim()),'ylim':list(ax.get_ylim()),'artist_values_exact':True})


# Bounding boxes retain the complete colored plot rectangles, including edge pixels.
# The colorbars are retained with their original tick values; scales differ by sample.
BOXES = {
    'gd1': [(161,195,1262,806),(1303,195,2404,806),(2467,220,2517,806)],
    'sid1': [(161,195,1262,806),(1303,195,2404,806),(2467,220,2517,806)],
    'b4': [(161,203,1262,798),(1303,203,2404,798),(2467,220,2517,806)],
    'clean1': [(123,157,979,614),(1009,157,1866,614),(1908,169,1950,616)],
    'bi2se3': [(161,189,1262,812),(1303,189,2404,812),(2467,220,2517,806)],
    'bi2te3': [(161,189,1262,812),(1303,189,2404,812),(2467,220,2517,806)],
}
BAR_TICKS = {'gd1':[354.5,546.5,723.5,797.0], 'sid1':[331.5,533.5,719.5,797.0],
             'b4':[283.0,506.5,711.5,797.0], 'clean1':[233.5,398.5,551.0,614.5],
             'bi2se3':[276.5,502.5,710.5,797.0], 'bi2te3':[289.5,510.0,712.5,797.0]}


def detector_pair(fig,key,x,width,outer,receipt):
    folder=ROOT/'figures/results_ordered/presentation_v10_cases' if key.startswith('bi2') else ASSETS
    path=folder/(STEMS[key]+'_detector.png')
    source=Image.open(path).convert('RGB')
    # Layout-only crops. The scientific RGB samples are not recolored or filtered.
    pair_width=width-.24
    gap=.055
    plane_w=(pair_width-gap)/2
    y=4.24
    for side,box in enumerate(BOXES[key][:2]):
        crop=source.crop(box)
        np.testing.assert_array_equal(np.asarray(crop),np.asarray(source)[box[1]:box[3],box[0]:box[2]])
        height=plane_w*crop.height/crop.width
        ax=fig.add_axes([(x+side*(plane_w+gap))/WIDTH,y/HEIGHT,plane_w/WIDTH,height/HEIGHT])
        ax.imshow(crop,interpolation='none',aspect='equal')
        ax.set_axis_off()
        title='Measured' if side==0 else ('Simulated*' if key=='clean1' else 'Simulated')
        fig.text((x+side*(plane_w+gap)+plane_w/2)/WIDTH,(y+height+.035)/HEIGHT,title,ha='center',va='bottom',fontsize=7)
        # Coordinates are read from retained source axes, not inferred from RGB intensity.
        if side==0 and outer:
            max_row=1704 if key.startswith('bi2') else (1668 if key in ('gd1','sid1') else 1620)
            for value in (0,800,1600):
                fig.text((x-.03)/WIDTH,(y+height*(1-value/max_row))/HEIGHT,str(value),ha='right',va='center',fontsize=6.5)
            for value in (0,1500,3000):
                fig.text((x+plane_w*value/3000)/WIDTH,(y-.025)/HEIGHT,str(value),ha='center',va='top',fontsize=6.5)
        receipt.append({'sample':key,'detector_side':side,'source_sha256':sha(path),'crop_box':box,'pixels_exact':True})
    box=BOXES[key][2]
    crop=source.crop(box)
    bar_h=.75
    bar_w=bar_h*crop.width/crop.height
    ax=fig.add_axes([(x+pair_width+.02)/WIDTH,(y+.005)/HEIGHT,bar_w/WIDTH,bar_h/HEIGHT])
    ax.imshow(crop,interpolation='none',aspect='equal')
    ax.set_axis_off()
    for value,source_y in zip((100,10,1,0),BAR_TICKS[key],strict=True):
        tick_y=y+.005+bar_h*(1-(source_y-box[1])/crop.height)
        fig.text((x+pair_width+.025+bar_w)/WIDTH,tick_y/HEIGHT,str(value),ha='left',va='center',fontsize=6)
    receipt.append({'sample':key,'colorbar_crop':box,'source_sha256':sha(path),'pixels_exact':True})


def shared_frames(keys,data,metadata):
    """Use real common limits before removing repeated numeric axes."""
    offaxis_edges=[]
    for key in keys:
        for name,spec in metadata['samples'][key]['branches'].items():
            if name=='m0':
                continue
            mask=data[f'{key}__comparison'][spec['start']:spec['stop']]
            indices=np.flatnonzero(mask)
            edges=spec['edges']
            offaxis_edges.extend((edges[indices[0]],edges[indices[-1]+1]))
    xoff=[min(offaxis_edges),max(offaxis_edges)]
    pad=.01*(xoff[1]-xoff[0])
    xoff=[xoff[0]-pad,xoff[1]+pad]
    frames={}
    for family in (1,3,4,0):
        names=['m0'] if family==0 else [f'm{family}_minus',f'm{family}_plus']
        scales={metadata['samples'][key]['scales'][name] for key in keys for name in names}
        scale='log' if scales=={'log'} else 'asinh'
        bounds=[metadata['samples'][key]['limits'][name]['y'] for key in keys for name in names]
        lower=min(b[0] for b in bounds)
        upper=max(b[1] for b in bounds)
        if len(scales)>1:
            # The mixed log/asinh 2H row uses signed asinh throughout. Include
            # every retained data/target value and the full uncertainty envelope.
            values=[]
            for key in keys:
                for name in names:
                    spec=metadata['samples'][key]['branches'][name]
                    sl=slice(spec['start'],spec['stop'])
                    mask=data[f'{key}__comparison'][sl]
                    y=data[f'{key}__data'][sl][mask]
                    sigma=data[f'{key}__sigma'][sl][mask]
                    values.extend((y-sigma,y+sigma,data[f'{key}__target'][sl][mask]))
            lower=min(lower,float(np.nanmin(np.concatenate(values))))
            upper=max(upper,float(np.nanmax(np.concatenate(values))))
        xlim=xoff
        if family==0:
            limits=[metadata['samples'][key]['limits']['m0']['x'] for key in keys]
            xlim=[min(v[0] for v in limits),max(v[1] for v in limits)]
        ticks=[5,10,15,20,25,30] if family==0 else ([2,6,10,14] if keys[0].startswith('bi2') else [1,2,3,4])
        frames[family]={'scale':scale,'x':xlim,'y':[lower,upper],
                        'ticks':[t for t in ticks if xlim[0]<=t<=xlim[1]]}
    return frames


def render(keys,stem,titles,data,metadata):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.linewidth':.55,
                         'axes.edgecolor':'#9aa2ab','text.color':'#151515','svg.fonttype':'none','pdf.fonttype':42})
    fig=plt.figure(figsize=(WIDTH,HEIGHT),facecolor='white')
    receipt=[]
    xstarts=[.52,3.84]
    group_width=3.16
    pw=(group_width-.055)/2
    stride=pw+.055
    frames=shared_frames(keys,data,metadata)
    row_axes={r:[] for r in frames}
    ordered=keys[0].startswith('bi2')
    for col,key in enumerate(keys):
        x=xstarts[col]
        heading=titles[col] if ordered else f'({chr(97+col)}) {titles[col]}'
        fig.text((x+group_width/2)/WIDTH,5.23/HEIGHT,heading,ha='center',va='center',fontsize=8.5,fontweight='bold')
        detector_pair(fig,key,x,group_width,col==0,receipt)
        for side in range(2):
            fig.text((x+side*stride+pw/2)/WIDTH,3.50/HEIGHT,'−' if side==0 else '+',ha='center',va='center',fontsize=9)
        for row,family in enumerate((1,3,4)):
            bottom=2.75-row*.685
            for side,sign in enumerate(('minus','plus')):
                ax=fig.add_axes([(x+side*stride)/WIDTH,bottom/HEIGHT,pw/WIDTH,.65/HEIGHT])
                profile(ax,key,f'm{family}_{sign}',data,metadata['samples'][key],frames[family],col==0 and side==0,row==2,receipt)
                row_axes[family].append(ax)
        ax=fig.add_axes([x/WIDTH,.26/HEIGHT,group_width/WIDTH,.74/HEIGHT])
        profile(ax,key,'m0',data,metadata['samples'][key],frames[0],col==0,True,receipt)
        row_axes[0].append(ax)
    # Every hidden vertical axis is identical to the visible left-hand axis.
    for axes in row_axes.values():
        for ax in axes[1:]:
            np.testing.assert_array_equal(ax.get_ylim(),axes[0].get_ylim())
            np.testing.assert_array_equal(ax.get_xlim(),axes[0].get_xlim())
            assert ax.get_yscale()==axes[0].get_yscale()
    fig.text(.025,4.65/HEIGHT,'Row (px)',ha='center',va='center',rotation=90,fontsize=6.5)
    fig.text(.52,4.04/HEIGHT,'Detector column (px)',ha='center',va='center',fontsize=6.5)
    for row,family in enumerate((1,3,4)):
        fig.text(.022,(3.075-row*.685)/HEIGHT,rf'$r={family}$',ha='center',va='center',rotation=90,fontsize=7)
    fig.text(.022,.63/HEIGHT,r'$r=0$',ha='center',va='center',rotation=90,fontsize=7)
    fig.text(.072,3.66/HEIGHT,'Net count / px²',ha='left',va='center',fontsize=7)
    fig.text(.52,1.16/HEIGHT,r'Projected $L$',ha='center',va='center',fontsize=7)
    fig.text(.52,.075/HEIGHT,r'Detector $2\theta$ (degrees)',ha='center',va='center',fontsize=7)
    handles=[Line2D([],[],color='#272e36',marker='.',ms=3,lw=.7,label='Data − background'),
             Line2D([],[],color='#df6800',ls='--',lw=.9,label='Illustrative overlay (not a fit)'),
             Patch(facecolor='#83909d',alpha=.45,label='±1σ band'),
             Patch(facecolor='#eeeeee',label='Excluded')]
    fig.legend(handles=handles,loc='center',bbox_to_anchor=(.52,3.83/HEIGHT),ncol=4,frameon=False,fontsize=6.6,
               handlelength=1.9,columnspacing=1.4,handletextpad=.45)
    parents=['Bi₂Se₃'] if ordered else (['2H'] if keys[0]=='gd1' else ['2H','6H','4H'])
    handles=[Line2D([],[],color=COLORS[p],lw=.7,ls='--',label=p) for p in parents]
    if ordered:
        handles[0].set_label('Ideal Bragg positions')
    fig.legend(handles=handles,loc='center',bbox_to_anchor=(.67,3.66/HEIGHT),ncol=len(parents),frameon=False,fontsize=6.6,
               handlelength=1.9,columnspacing=.9,handletextpad=.4)
    if not ordered:
        fig.text(.50,3.66/HEIGHT,'Bragg guides:',fontsize=6.6,ha='right',va='center')
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    for text in fig.texts:
        bounds=text.get_window_extent(renderer)
        assert bounds.x0>=0 and bounds.y0>=0 and bounds.x1<=fig.bbox.width and bounds.y1<=fig.bbox.height,text.get_text()
    OUT.mkdir(parents=True,exist_ok=True)
    for ext in ('pdf','svg','png'):
        fig.savefig(OUT/f'{stem}.{ext}',dpi=360)
    target=ROOT/('figures/results_ordered' if ordered else 'figures/results_pbi2')/f'{stem}.pdf'
    target.write_bytes((OUT/f'{stem}.pdf').read_bytes())
    plt.close(fig)
    return {'figure':stem,'size_inches':[WIDTH,HEIGHT],'shared_frames':frames,
            'shared_axes_verified':True,'checks':receipt,'pdf_sha256':sha(target)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args()
    if args.archive:
        freeze_inputs(args.archive)
    metadata=json.loads((INPUT/'metadata.json').read_text(encoding='utf-8'))
    assert sha(INPUT/'profiles.npz')==metadata['profiles_sha256']
    with np.load(INPUT/'profiles.npz') as data:
        records=[render(('gd1','sid1'),'pbi2_2h_compact',('GD1 · little mosaic disorder','SiD1 · strong mosaic disorder'),data,metadata),
                 render(('b4','clean1'),'pbi2_polytypes_compact',('B4 · 2H + 6H','Clean1 · 2H + 6H + 4H'),data,metadata),
                 render(('bi2se3','bi2te3'),'bi2x3_compact',('Bi₂Se₃','Bi₂Te₃'),data,metadata)]
    (OUT/'verification.json').write_text(json.dumps({'figures':records,'source_metadata_sha256':sha(INPUT/'metadata.json'),
        'limitations':'Detector colors and source colorbars preserved as RGB, not reconstructed counts. Profile targets remain editorial, not fits. Clean1 simulation remains a visual edit.'},indent=2),encoding='utf-8')
    print('Three comparison figures exported; shared-axis, exact profile artist and detector crop checks passed.')


if __name__=='__main__':
    main()
