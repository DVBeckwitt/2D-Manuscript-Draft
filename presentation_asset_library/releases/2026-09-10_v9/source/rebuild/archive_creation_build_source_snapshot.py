from pathlib import Path
import hashlib,json,shutil,re,os,sys,zipfile
ROOT=Path.cwd(); LIB=ROOT/'presentation_asset_library/releases/2026-09-10_v9'; OUT=LIB/'source'; OUT.mkdir(parents=True,exist_ok=True)
records=[]; omitted=[]; missing=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def add(p,target=None,role='original source snapshot'):
 p=Path(p)
 if not p.is_file(): missing.append(str(p));return
 if target is None:
  try:rel=Path('workspace')/p.resolve().relative_to(ROOT)
  except ValueError:
   rel=Path('external')/Path(*p.resolve().parts[1:])
 else:rel=Path(target)
 dest=OUT/rel; dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(p,dest)
 records.append({'original_path':str(p.resolve()),'archived_path':str(dest.relative_to(LIB)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(dest),'role':role})
seen=set()
source_ext={'.py','.mjs','.js','.json','.md','.csv','.toml','.yaml','.yml','.html','.svg','.bin','.txt'}
root=ROOT/'build_codex/slate_talk'
for p in root.rglob('*'):
 if not p.is_file() or any(x in p.parts for x in ['node_modules','__pycache__','bin','obj','frames','source_renders','final_renders','preview_renders']):continue
 if p.suffix in source_ext and not any(x in str(p).lower() for x in ['invalid_media_id_removed','chart-data-snapshot','inspection','runtime_patch']):
  add(p);seen.add(p.resolve())
npz=[p for p in root.rglob('*.npz') if ('animated_deck_v8' in p.parts and p.name not in ['pilot.npz']) or 'se_retained' in p.parts or p.name in ['profile_grid.npz','pbi2_m1_curves.npz','footprint_arrays.npz']]
for p in npz:add(p,role='direct numeric arrays and final simulation intermediates');seen.add(p.resolve())
# Rendering input snapshots and exact source user edits.
for name in ['sample_rotation_reciprocal_rings_indexed_still.png','ewald_intersections_then_mosaic_clean_end_still.png','ewald_traces_to_detector_still.png','ewald_traces_to_detector_labeled_still.png','detector_to_qz_qr_labeled_still.png','pbi2_general_stacking_disorder_still.png']:
 add(ROOT/'output/presentations/animations'/name,role='animation chaining input')
for p in (root/'animated_deck_v7/diagnostics').glob('te_*.png'):add(p,role='preferred final Te figure source crop')
for p in (root/'animated_deck_v9/figures/se_retained').glob('*.png'):add(p,role='preferred final Se figure source crop')
p=Path('C:/Users/Kenpo/Downloads/Oriented_Powder_8min_Animated_v8.pptx')
assert sha(p)=='03f7c853bc92153c675364db5a4f9aa055c5c488a8b17a9d6cf98614ae4e8136'
add(p,'original_presentation/User_edited_v8_source.pptx','exact user-edited source of final v9; not interchangeable with project v8')
# Bound external dependency collection: only exact file references in pertinent manifests, no directory crawls.
seed=[root/'best_fit_parameters/fit_selection.private.json',root/'best_fit_parameters/library_candidates.private.json',root/'best_fit_parameters/mosaic_curves.private.json',root/'termination_comparison/termination_parallel_direct_export.private.json',root/'termination_figure/termination_direct_export.private.json',root/'animated_deck_v7/diagnostics/diagnostic_crops_manifest.private.json',root/'animated_deck_v9/figures/se_retained/se_retained_profiles_manifest.private.json']
def walk(v):
 if isinstance(v,dict):
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
 elif isinstance(v,str) and re.match(r'^[A-Za-z]:[\\/]',v):yield v
for p in seed:
 for value in walk(json.loads(p.read_text(encoding='utf-8-sig'))):
  q=Path(value)
  if not q.is_file() or q.resolve() in seen:continue
  if q.suffix.lower() not in source_ext|{'.npz','.cif','.png','.pkl'}:continue
  seen.add(q.resolve())
  if q.stat().st_size>20_000_000:
   omitted.append({'original_path':str(q),'bytes':q.stat().st_size,'reason':'large intermediate; final displayed arrays and direct exports preserved independently'});continue
  add(q,role='exact manifest-referenced external dependency')
# Small external renderer sources and optical data.
v=Path('C:/Users/Kenpo/.codex/visualizations/2026/09')
extras=[v/'05/specular_restore/restore_specular.py',v/'05/background_correction/correct_backgrounds.py',v/'04/bi2x3_requested_regions/render_current_continuous_regions.py',v/'04/all_materials_log/render_remaining_materials.py']
extras += [v/f'05/specular_restore/{material}_specular{ext}' for material in ['bi2se3','bi2te3'] for ext in ['.json','.ra_diag.npz']]
extras += list(Path('C:/Users/Kenpo/Downloads/2D_Manuscript/figures/bi2te3_spatial_fit_2026_09_10').glob('*.png'))
for p in extras:
 if p.resolve() not in seen:add(p,role='external figure or optical replay source');seen.add(p.resolve())
# Capture actual checked-out numerical engine source and license/packaging, not the environment/compiled caches.
for dirname in ['SLATE-rMC-bi2x3-polar-line-refit','SLATE-rMC']:
 eng=ROOT.parent/dirname
 for sub in ['src','scripts']:
  for p in (eng/sub).rglob('*'):
   if p.is_file() and not any(x in p.parts for x in ['__pycache__','node_modules','.git']) and p.suffix in {'.py','.pyi','.cif','.toml','.json','.yaml'} and p.stat().st_size<2000000:
    if p.resolve() not in seen:add(p,Path('engines')/dirname/p.relative_to(eng),'numerical engine source snapshot; full simulation relocation unverified');seen.add(p.resolve())
 for name in ['LICENSE','LICENSE.md','LICENSE.txt','COPYING','pyproject.toml','requirements.txt','README.md','uv.lock']:
  p=eng/name
  if p.exists():add(p,Path('engines')/dirname/name,'engine license or package metadata')
# Preserve relevant source docs.
for name in ['MANUSCRIPT_STATUS.md','AGENTS.md']:
 add(ROOT/name,Path('context')/name,'context snapshot at release; canonical ongoing status remains in project root')
manifest={'schema':'oriented-powder-source-snapshot.v1','release':'2026-09-10_v9','source_files':records,'source_file_count':len(records),'source_bytes':sum(r['bytes'] for r in records),'omitted_large_intermediates':omitted,'missing_explicit_inputs':sorted(set(missing)),'portability':'Viewing is independent of original paths. Numeric figure adapters use compact direct inputs. Original generators intentionally retain source paths; complete simulation refitting has not been rerun from this archive.'}
(LIB/'provenance').mkdir(parents=True,exist_ok=True);(LIB/'provenance/source_snapshot.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['source_files']},indent=2))

