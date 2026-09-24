from pathlib import Path
import json,pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator,FuncFormatter,NullLocator
ROOT=Path(r'C:\Users\Kenpo\.codex\visualizations\2026\09\06\01a0790a-e521-7951-8cf8-97659242b079');OUT=ROOT/'bi2te3_joint_roi_20260910'
FIG=Path(r'C:\Users\Kenpo\Downloads\2D_Manuscript\figures\bi2te3_spatial_fit_2026_09_10')
def divide(value,area):
    return np.divide(value,area,out=np.full_like(value,np.nan,dtype=float),where=area>0)
def run():
    with np.load(str(OUT)+'.ra_diag.npz') as z:
        keys=['joint_parent','joint_radial','joint_measured','joint_background','joint_selected','joint_area','joint_parent_density_area','joint_valid','joint_count_covariance','joint_background_modes']
        a={k:z[k] for k in keys};edges={n:z[f'joint_{n}_fine_report_edges'] for n in ('m1_minus','m1_plus')}
    m=json.loads(Path(str(OUT)+'.json').read_text())
    assert m['active_fit_response']['generation']=='gh5' and m['joint_search']['strict_joint_roi_selection']
    packet=pickle.loads((ROOT.parent/'full_physical_intensity_refit/bi2te3_inputs.pkl').read_bytes())
    parent=a['joint_parent'];n=len(parent);G=np.zeros((800,n));G[parent,np.arange(n)]=1
    area=a['joint_parent_density_area'];bg=a['joint_background'];C=a['joint_count_covariance']+a['joint_background_modes'].T@a['joint_background_modes']
    observed=divide(G@(a['joint_measured']-bg),area);fit=divide(G@(a['joint_selected']-bg),area)
    sig=divide(np.sqrt(np.maximum(np.diag(G@C@G.T),0)),area)
    theta=packet['regions']['m0']['theta_deg']
    colors={'data':'#243445','fit':'#e76f16'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#a8b0bd','axes.labelcolor':colors['data'],'text.color':colors['data'],'savefig.facecolor':'white'})
    FIG.mkdir(parents=True,exist_ok=True)
    handles=[Line2D([0],[0],color=colors['data'],marker='o',ms=4,lw=1,label='Measured minus background'),
             Line2D([0],[0],color=colors['fit'],lw=2,label='Current physical fit')]
    def header(fig,title,subtitle):
        fig.suptitle(title,x=.08,y=.984,ha='left',fontsize=22,fontweight='bold')
        fig.text(.08,.984-.50/fig.get_figheight(),subtitle,fontsize=11,color='#596779')
        fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,.984-.82/fig.get_figheight()),ncol=2,frameon=False)
    def style(ax):
        ax.set_yscale('asinh',linear_width=3);ax.axhline(0,color='#aebbc8',lw=.7);ax.grid(alpha=.16)
        vals=np.array([3,10,30,100,300,1000,3000,10000,30000,100000.]);low,high=ax.get_ylim()
        ticks=np.r_[-vals[::-1],0,vals];ticks=ticks[(ticks>=low)&(ticks<=high)]
        if len(ticks)>12:
            vals=vals[::2];ticks=np.r_[-vals[::-1],0,vals];ticks=ticks[(ticks>=low)&(ticks<=high)]
        ax.yaxis.set_major_locator(FixedLocator(ticks));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:g}'));ax.yaxis.set_minor_locator(NullLocator())
    def plot(ax,x,ix):
        ax.errorbar(x,observed[ix],yerr=sig[ix],color=colors['data'],marker='o',ms=3,lw=1,capsize=1.5,zorder=3)
        ax.plot(x,fit[ix],color=colors['fit'],lw=2,zorder=2)
        style(ax);ax.set_ylabel('Net counts / pixel area')
    def equalize(pair):
        lo=min(ax.get_ylim()[0] for ax in pair);hi=max(ax.get_ylim()[1] for ax in pair)
        for ax in pair:ax.set_ylim(lo,hi);style(ax)
    subtitle='Analytic beam-position integration; shared mosaic and surface parameters retained.'
    foot='Asinh axes retain faint peaks and negative data. Error bars: count + background uncertainty scale, not confidence intervals.'
    def save(fig,name):
        fig.savefig(FIG/name,dpi=180);plt.close(fig)
    fig=plt.figure(figsize=(14,13));gs=fig.add_gridspec(3,2,height_ratios=(1.15,1,1))
    ax=fig.add_subplot(gs[0,:]);plot(ax,theta,np.arange(510,800));ax.set_xlim(1,30)
    ax.set_title('m = 0 | full detector angle range',loc='left');ax.set_xlabel(r'Detector $2\theta$ (degrees)')
    pairs=[]
    for j,(name,off,label) in enumerate([('m1_minus',0,'m = 1, minus side'),('m1_plus',85,'m = 1, plus side'),('m3_minus',170,'m = 3, minus side'),('m3_plus',255,'m = 3, plus side')]):
        ax=fig.add_subplot(gs[1+j//2,j%2]);plot(ax,packet['regions'][name]['L'],off+np.arange(85))
        ax.set_xlim(0,17);ax.set_title(label,loc='left');ax.set_xlabel('L along reciprocal rod');pairs.append(ax)
    equalize(pairs[:2]);equalize(pairs[2:]);header(fig,'Bi2Te3 | current physical fit',subtitle)
    fig.subplots_adjust(left=.08,right=.98,bottom=.08,top=.83,hspace=.47,wspace=.23)
    fig.text(.08,.029,foot,fontsize=9,color='#596779');fig.text(.08,.013,'No joint parameter improvement selected. Curves are ROI-bin averages; no smoothing or clipping applied.',fontsize=9,color='#596779')
    save(fig,'bi2te3_current_physical_fit.png')
    fig,axes=plt.subplots(3,2,figsize=(14,12))
    for row,center in enumerate((5.,10.,11.)):
        for col,(name,off,side) in enumerate([('m1_minus',0,'minus'),('m1_plus',85,'plus')]):
            L=packet['regions'][name]['L'];take=np.flatnonzero(abs(L-center)<=1.6)
            ax=axes[row,col];plot(ax,L[take],off+take);ax.set_xlim(center-1.6,center+1.6)
            ax.set_title(f'm = 1, {side} side | L = {center:g}',loc='left');ax.set_xlabel('L along reciprocal rod')
        equalize(axes[row])
    header(fig,'Bi2Te3 | m = 1 peak cores and tails',subtitle)
    fig.subplots_adjust(left=.08,right=.98,bottom=.08,top=.82,hspace=.45,wspace=.24);fig.text(.08,.025,foot,fontsize=9,color='#596779')
    save(fig,'bi2te3_joint_tails.png')
    fig,axes=plt.subplots(2,2,figsize=(14,10))
    for row,center in enumerate((5.,10.)):
        for col,(name,off,side) in enumerate([('m1_minus',0,'minus'),('m1_plus',85,'plus')]):
            L=packet['regions'][name]['L'];parents=off+np.flatnonzero(abs(L-center)<.2+1e-8)
            T=np.zeros((10,n))
            for j in range(10):T[j,np.isin(parent,parents)&(a['joint_radial']==j)&a['joint_valid']]=1
            ar=T@a['joint_area'];y=divide(T@(a['joint_measured']-bg),ar);f=divide(T@(a['joint_selected']-bg),ar)
            error=divide(np.sqrt(np.maximum(np.diag(T@C@T.T),0)),ar);e=edges[name];x=(e[:-1]+e[1:])/2;ax=axes[row,col]
            ax.errorbar(x,y,xerr=np.diff(e)/2,yerr=error,color=colors['data'],marker='o',ms=4,lw=1,capsize=2)
            ax.stairs(f,e,color=colors['fit'],lw=2,baseline=None);style(ax)
            ax.set_title(f'm = 1, {side} side | L = {center:g} +/- 0.2',loc='left')
            ax.set_xlabel(r'$Q_r$ (inverse angstrom)');ax.set_ylabel('Net counts / pixel area')
        equalize(axes[row])
    header(fig,'Bi2Te3 | widths across the rods','The same joint observations, viewed across Qr. These cuts add no duplicate fit weight.')
    fig.subplots_adjust(left=.08,right=.98,bottom=.1,top=.81,hspace=.42,wspace=.25);fig.text(.08,.035,foot,fontsize=9,color='#596779')
    save(fig,'bi2te3_joint_across.png')
    fig,axes=plt.subplots(2,1,figsize=(14,8),gridspec_kw={'height_ratios':[3,1]})
    plot(axes[0],theta,np.arange(510,800));axes[0].set_xlim(1,30);axes[0].set_xlabel('')
    axes[1].plot(theta,(observed[510:800]-fit[510:800])/sig[510:800],color=colors['data'],lw=1)
    axes[1].axhline(0,color='#aebbc8',lw=.7);axes[1].set_xlim(1,30);axes[1].grid(alpha=.16)
    axes[1].set_xlabel(r'Detector $2\theta$ (degrees)');axes[1].set_ylabel('Residual /\nuncertainty scale')
    header(fig,'Bi2Te3 | full m = 0 profile',subtitle)
    fig.subplots_adjust(left=.08,right=.98,bottom=.12,top=.8,hspace=.12);fig.text(.08,.032,foot,fontsize=9,color='#596779')
    save(fig,'bi2te3_joint_m0_full.png')
    assert np.all(np.isfinite(fit[area>0]))
    print(json.dumps({'paths':[str(FIG/k) for k in ('bi2te3_current_physical_fit.png','bi2te3_joint_tails.png','bi2te3_joint_across.png','bi2te3_joint_m0_full.png')]}))
if __name__=='__main__':run()
