"""Verify the continuous opening against direct coherent-amplitude sums."""
from pathlib import Path
import hashlib,json
import numpy as np
import cylinder_bridge as cb
import animate_bridge as animation

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    grid=np.unique(np.r_[np.linspace(.15,3.55,1201),1+np.linspace(-.02,.02,1201)])
    max_error=0.;max_area=0.;max_jump=0.
    means=[8.,8.1,8.5,8.999,9.,16.5,32.,64.25,128.,511.9,512.]
    for mean in means:
        m=int(np.floor(mean));f=mean-m
        # Independent unnormalized coherent amplitudes; mix intensities first.
        a=np.exp(2j*np.pi*grid[:,None]*np.arange(m)).sum(axis=1)
        b=np.exp(2j*np.pi*grid[:,None]*np.arange(m+1)).sum(axis=1)
        peak=(1-f)*m*m+f*(m+1)*(m+1)
        expected=((1-f)*abs(a)**2+f*abs(b)**2)/peak
        actual=cb.thickness_population_profile(grid,mean)
        max_error=max(max_error,float(np.max(abs(actual-expected))))
        assert actual.min()>=0 and actual.max()<=1+1e-12
        period=cb.thickness_population_profile(np.arange(4096)/4096,mean)
        max_area=max(max_area,abs(float(period.mean())-mean/peak))
    for m in [9,16,32,64,128]:
        left=cb.thickness_population_profile(grid,m-1e-8)
        right=cb.thickness_population_profile(grid,m+1e-8)
        max_jump=max(max_jump,float(np.max(abs(left-right))))
    assert max_error<1e-10 and max_area<1e-12 and max_jump<1e-7
    assert cb.opening_layer_count(0)==512 and cb.opening_layer_count(1)==8
    times=np.array([2.,3.,4.,5.,6.])
    widths=np.array([1/cb.opening_layer_count(animation.state(t)[1]) for t in times])
    assert np.all(np.diff(widths)>0) and np.all(np.diff(widths,2)>0)
    narrow_L,narrow_S=cb.opening_profile_data(512)
    half_count=int(((abs(narrow_L-1)<.01)&(narrow_S>=.5)).sum())
    assert half_count>=16
    npz=np.load(ROOT/'data/opening_profiles.npz')
    assert all(np.isfinite(npz[k]).all() for k in npz.files)
    report={'status':'PASS','direct_coherent_sum_max_error':max_error,
        'mixture_period_area_max_error':max_area,'integer_boundary_difference_at_plus_minus_1e_8':max_jump,
        'initial_mean_layers':512,'final_mean_layers':8,'N512_samples_inside_half_height':half_count,
        'pacing':'Inverse mean thickness, hence visible width, accelerates over the opening. This is not a claim of accelerating physical layer-removal rate.',
        'normalization':'Neighboring integer intensities mixed before peak normalization; period area is mean/peak, not generally1/mean.',
        'scope':'Illustrative geometry and thickness population, not a new material fit.',
        'files':{name:sha(ROOT/name) for name in ['source/cylinder_bridge.py','source/animate_bridge.py',
            'data/opening_profiles.npz','data/model_arrays.npz','caption.txt']}}
    (ROOT/'provenance/science_review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
