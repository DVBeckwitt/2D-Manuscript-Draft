"""Compare decoded retained slide pixels against immutable v9 exports."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = ROOT / 'presentation_asset_library/releases/2026-09-10_v9/slides'
NEW = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / 'final_renders'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

comparisons = []
for old_no in range(1, 26):
    new_no = old_no if old_no < 19 else old_no + 1
    old = OLD / f'slide-{old_no:02d}.png'
    new = NEW / f'slide-{new_no:02d}.png'
    a, b = Image.open(old).convert('RGB'), Image.open(new).convert('RGB')
    size_equal = a.size == b.size
    exact = size_equal and a.tobytes() == b.tobytes()
    delta = ImageChops.difference(a, b).getbbox() if size_equal and not exact else None
    comparisons.append({'source_slide': old_no, 'target_slide': new_no,
        'pixel_identical': exact, 'png_byte_identical': old.read_bytes() == new.read_bytes(),
        'source_size': a.size, 'target_size': b.size, 'difference_bounds': delta,
        'source_png_sha256': sha(old), 'target_png_sha256': sha(new)})

new_slide = NEW / 'slide-19.png'
with Image.open(new_slide) as im:
    size = im.size
status = all(c['pixel_identical'] for c in comparisons) and size == (1920, 1080)
receipt = {'status': 'pass' if status else 'fail', 'method': 'Exact decoded RGB pixel bytes',
    'reference': str(OLD), 'candidate': str(NEW), 'retained_slide_comparisons': comparisons,
    'new_slide_19_size': size, 'new_slide_19_sha256': sha(new_slide),
    'new_slide_visual_review': 'Recorded separately after image inspection',
    'render_scope': 'Static ArtifactTool render, not PowerPoint movie playback'}
(HERE / 'independent_render_audit.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'status': receipt['status'], 'pixel_identical_retained_slides': sum(c['pixel_identical'] for c in comparisons),
    'new_slide_size': size}, indent=2))
sys.exit(0 if status else 1)
