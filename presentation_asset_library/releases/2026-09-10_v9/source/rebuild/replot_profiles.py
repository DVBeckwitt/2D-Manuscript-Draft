"""Replot archived Se and Te profiles without the original machine or fit banks.

Usage: python replot_profiles.py --material se --output /path/to/new/output
Use Matplotlib3.10.3 for Se; Matplotlib3.11.1 for Te.
Requires numpy, matplotlib and Pillow. Does not refit or modify the archive.
"""
from pathlib import Path
import argparse, importlib.util, json, sys, types, hashlib
from PIL import Image
sys.dont_write_bytecode = True

SOURCE=Path(__file__).resolve().parents[1]
RELEASE=SOURCE.parent

def external(original):
    manifest=json.loads((RELEASE/'provenance/source_snapshot.json').read_text(encoding='utf-8'))
    wanted=original.replace('\\','/').lower()
    row=next(r for r in manifest['source_files'] if r['original_path'].replace('\\','/').lower()==wanted)
    return RELEASE/row['archived_path']

def compare(path,reference):
    with Image.open(path) as a, Image.open(reference) as b:
        same=a.size==b.size and a.convert('RGBA').tobytes()==b.convert('RGBA').tobytes()
    return {'output':str(path),'reference':str(reference.relative_to(RELEASE)), 'pixel_equal':same}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--material',choices=['se','te'],required=True);args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if out==RELEASE or RELEASE in out.parents:
        raise SystemExit('Choose an output directory outside the immutable release.')
    workspace=SOURCE/'workspace/build_codex/slate_talk'; reports=[]
    if args.material=='se':
        src=workspace/'animated_deck_v9/figures/render_se_retained_profiles.py'
        spec=importlib.util.spec_from_file_location('archived_se_replot',src);se=importlib.util.module_from_spec(spec);spec.loader.exec_module(se)
        se.ROOT=out/'se';se.SOURCE=external('C:/Users/Kenpo/.codex/visualizations/2026/09/05/specular_restore/bi2se3_specular.ra_diag.npz');se.META=external('C:/Users/Kenpo/.codex/visualizations/2026/09/05/specular_restore/bi2se3_specular.json');se.main()
        for name in ['se_axial_full_00l.png','se_r1_minus.png','se_r1_plus.png','se_legend.png']:
            reports.append(compare(se.ROOT/name,workspace/'animated_deck_v9/figures/se_retained'/name))
    if args.material=='te':
        # Only data loading is adapted. The numerical aggregation, plotting and styles
        # below remain the exact generator recovered from its source archive.
        te_dir=SOURCE/'direct_data/te_profiles';original=(te_dir/'original_spatial_final_figure.py').read_text(encoding='utf-8')
        old="packet=pickle.loads((ROOT.parent/'full_physical_intensity_refit/bi2te3_inputs.pkl').read_bytes())"
        new="packet={'regions': {name: {k:np.asarray(v) for k,v in region.items()} for name,region in json.loads((ROOT/'coordinates.json').read_text()).items()}}"
        assert original.count(old)==1, 'Original data loader unexpectedly changed'
        te=types.ModuleType('archived_te_replot');te.__file__=str(te_dir/'original_spatial_final_figure.py');exec(compile(original.replace(old,new),te.__file__,'exec'),te.__dict__)
        te.ROOT=te_dir;te.OUT=te_dir/'bi2te3_profiles';te.FIG=out/'te';te.run()
        source=external('C:/Users/Kenpo/Downloads/2D_Manuscript/figures/bi2te3_spatial_fit_2026_09_10/bi2te3_current_physical_fit.png')
        reports.append(compare(te.FIG/'bi2te3_current_physical_fit.png',source))
        boxes={'te_axial_full_00l.png':(25,340,2510,982),'te_r1_minus.png':(25,1038,1260,1617),'te_r1_plus.png':(1280,1038,2510,1617),'te_legend.png':(25,192,2510,253),'te_source_footnotes.png':(150,2245,2470,2325)}
        with Image.open(te.FIG/'bi2te3_current_physical_fit.png') as im:
            for name,box in boxes.items():
                im.crop(box).save(te.FIG/name);reports.append(compare(te.FIG/name,workspace/'animated_deck_v7/diagnostics'/name))
    record={'schema':'oriented-powder-replot-verification.v1','material':args.material,'all_pixel_equal':all(r['pixel_equal'] for r in reports),'comparisons':reports,'note':'Pixel identity depends on Matplotlib/Pillow/font versions. Data and checksums are authoritative across runtimes; outputs never overwrite the archived final.'}
    (out/'profile_replot_verification.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record,indent=2))
    if not record['all_pixel_equal']:raise SystemExit('Replot differs at pixel level; see verification file. Archived final files remain unchanged.')

if __name__=='__main__':main()
