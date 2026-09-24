from pathlib import Path
import sys,pathlib,pickle,hashlib,json,zipfile,csv
import numpy as np
ROOT=Path.cwd();REL=ROOT/'presentation_asset_library/releases/2026-09-10_v9';OUT=REL/'source/direct_data/te_profiles';OUT.mkdir(parents=True,exist_ok=True)
sys.path[:0]=['C:/Users/Kenpo/Nextcloud/Git Projects/SLATE-rMC-bi2x3-polar-line-refit/src','C:/Users/Kenpo/Nextcloud/Git Projects/SLATE-rMC']
class Compat(pickle.Unpickler):
 def find_class(self,module,name):
  if module=='pathlib._local':return getattr(pathlib,name)
  return super().find_class(module,name)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
 return h.hexdigest()
packetp=Path('C:/Users/Kenpo/.codex/visualizations/2026/09/06/full_physical_intensity_refit/bi2te3_inputs.pkl')
with packetp.open('rb') as f:packet=Compat(f).load()
npzp=Path('C:/Users/Kenpo/.codex/visualizations/2026/09/06/01a0790a-e521-7951-8cf8-97659242b079/bi2te3_joint_roi_20260910.ra_diag.npz')
keys=['joint_parent','joint_radial','joint_measured','joint_background','joint_selected','joint_area','joint_parent_density_area','joint_valid','joint_count_covariance','joint_background_modes']+[f'joint_{n}_fine_report_edges' for n in ('m1_minus','m1_plus')]
with np.load(npzp,allow_pickle=False) as z:
 a={k:z[k] for k in keys}
 original=z['spatial_final_figure_source_bytes'].tobytes().decode('utf8')
(OUT/'original_spatial_final_figure.py').write_bytes(original.encode('utf8'))
np.savez_compressed(OUT/'bi2te3_profiles.ra_diag.npz',**a)
coords={name:{k:v.tolist() for k,v in region.items() if k in ['L','theta_deg']} for name,region in packet['regions'].items()}
(OUT/'coordinates.json').write_text(json.dumps(coords,indent=2),encoding='utf8')
source_record=ROOT/'build_codex/slate_talk/animated_deck_v7/diagnostics/te_source_record.private.json'
(OUT/'bi2te3_profiles.json').write_bytes(source_record.read_bytes())
# Exact same linear aggregation and covariance formula as archived final figure generator.
parent=a['joint_parent'];n=len(parent);G=np.zeros((800,n));G[parent,np.arange(n)]=1
area=a['joint_parent_density_area'];bg=a['joint_background'];C=a['joint_count_covariance']+a['joint_background_modes'].T@a['joint_background_modes']
divide=lambda x:np.divide(x,area,out=np.full_like(x,np.nan,dtype=float),where=area>0)
observed=divide(G@(a['joint_measured']-bg));fit=divide(G@(a['joint_selected']-bg));sig=divide(np.sqrt(np.maximum(np.diag(G@C@G.T),0)))
direct={}
for name,ix in [('m1_minus',np.arange(85)),('m1_plus',85+np.arange(85)),('m3_minus',170+np.arange(85)),('m3_plus',255+np.arange(85)),('m0',np.arange(510,800))]:
 direct.update({name+'_x':np.asarray(coords[name]['theta_deg' if name=='m0' else 'L']),name+'_net_measured':observed[ix],name+'_net_model':fit[ix],name+'_uncertainty_scale':sig[ix],name+'_area':area[ix]})
np.savez_compressed(OUT/'bi2te3_displayed_profiles_direct.npz',**direct)
arraysmeta=[]
with (OUT/'bi2te3_displayed_profiles.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['branch','bin','x','x_unit','net_measured_counts_per_pixel_area','net_model_counts_per_pixel_area','uncertainty_scale_counts_per_pixel_area','normalizing_pixel_area'])
 for name in ['m1_minus','m1_plus','m3_minus','m3_plus','m0']:
  for i in range(len(direct[name+'_x'])):
   vals=[direct[name+'_'+k][i] for k in ['x','net_measured','net_model','uncertainty_scale','area']]
   w.writerow([name,i,format(vals[0],'.17g'),'detector_2theta_degrees' if name=='m0' else 'L_reciprocal_lattice_units',*[format(v,'.17g') for v in vals[1:]]])
metadata={'schema':'oriented-powder-compact-te-profiles.v1','source_npz':str(npzp),'source_npz_bytes':npzp.stat().st_size,'source_npz_sha256':sha(npzp),'source_packet':str(packetp),'source_packet_sha256':sha(packetp),'compact_array_keys':{k:{'shape':list(v.shape),'dtype':str(v.dtype),'raw_c_order_sha256':hashlib.sha256(v.tobytes()).hexdigest()} for k,v in a.items()},'original_generator_sha256':hashlib.sha256(original.encode()).hexdigest(),'coordinate_operation':'Exact L/theta coordinate arrays extracted from source packet. No pickle needed to rebuild figures.','array_operation':'Exact selected arrays copied without any recomputation. Displayed curves and uncertainty use the original generator linear aggregation and covariance formula.','csv_precision':'.17g IEEE754 binary64 round-trip; nan is retained, no values clipped','limitations':['Conditional spatial-integration model, no accepted new joint best fit.','Original full numerical integration bank omitted (5.97GB); original source hash retained.','Error bars are count+background uncertainty scale, not confidence intervals.','Replot equivalence must be verified against exact recorded source PNG before asserting current archived arrays match prior figure.']}
(OUT/'data_dictionary.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
# Open-format Se export preserves all source quantities and valid masks.
se=REL/'source/workspace/build_codex/slate_talk/animated_deck_v9/figures/se_retained/bi2se3_retained_profiles_direct.npz';sd=REL/'source/direct_data/se_profiles';sd.mkdir(parents=True,exist_ok=True)
with np.load(se,allow_pickle=False) as z:
 fields=['x','valid','measured','background','net_measured','model_total','net_model']
 with (sd/'bi2se3_displayed_profiles.csv').open('w',newline='',encoding='utf8') as f:
  w=csv.writer(f);w.writerow(['branch','bin','x_unit',*fields])
  for name in ['m1_minus','m1_plus','m3_minus','m3_plus','m0']:
   for i in range(len(z[name+'_x'])):w.writerow([name,i,'detector_2theta_degrees' if name=='m0' else 'L_reciprocal_lattice_units',*[str(int(z[name+'_'+k][i])) if k=='valid' else format(z[name+'_'+k][i],'.17g') for k in fields]])
 (sd/'data_dictionary.json').write_text(json.dumps({'schema':'oriented-powder-se-profiles-csv.v1','source_npz':str(se.relative_to(REL)),'source_sha256':sha(se),'array_shapes':{k:list(z[k].shape) for k in z.files},'counts_unit':'counts per pixel area','x_unit':'m0 detector2theta degrees; other branches L reciprocal-lattice units','valid':'1=evaluated valid bin,0=invalid; no implicit dropping','csv_precision':'.17g IEEE754 binary64 round-trip; negative values and nan retained','uncertainty':'Unavailable; no manufactured error bars'},indent=2),encoding='utf8')
print(json.dumps({'te_compact_bytes':sum(p.stat().st_size for p in OUT.iterdir()),'Te_source_hash':metadata['source_npz_sha256'],'te_direct':str(OUT),'se_csv':str(sd)}))
