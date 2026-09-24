"""Build the local animation gallery without external resources."""
from pathlib import Path
import html
ROOT=Path(__file__).resolve().parents[1]

def main():
    caption=html.escape((ROOT/'caption.txt').read_text(encoding='utf-8').strip())
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cylinder bridge v3</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f1f5f7;color:#233442;font:16px/1.6 system-ui,sans-serif}main{max-width:1140px;margin:auto;padding:40px 26px}h1{font-size:clamp(29px,4vw,44px);line-height:1.16}h2{font-size:25px}.eyebrow{color:#087f8c;text-transform:uppercase;letter-spacing:.09em;font-size:13px;font-weight:700}article{background:white;border:1px solid #dbe4e8;border-radius:8px;padding:28px;margin:28px 0}video,img{display:block;width:100%;height:auto}a{color:#087f8c;text-underline-offset:3px}.links{display:flex;flex-wrap:wrap;gap:20px;margin:20px 0}.caption{font-size:14px;color:#536674}@media(max-width:600px){main{padding:25px 12px}article{padding:15px}}</style>
<main><header><div class="eyebrow">Bi₂Se₃ / Bi₂Te₃ → geometry → PbI₂</div><h1>From Bragg peaks<br>to diffraction cylinders</h1><p>Very sharp peaks widen smoothly as the stack thins. The broadening speeds up toward the end, then the cylinder, mosaic and Ewald sequence continues.</p><div class="links"><a href="README.md">Source and rebuild guide</a></div></header>
<article><div class="eyebrow">26-second animation · version 3</div><h2>A smoother start</h2><video controls playsinline preload="metadata" poster="storyboard/frame_00.0s.png"><source src="Cylinder_Bridge.mp4" type="video/mp4"></video><div class="links"><a href="Cylinder_Bridge.mp4" download>Download MP4</a><a href="Cylinder_Bridge_poster.png">Final Ewald frame</a></div></article>
<article><div class="eyebrow">Companion manuscript figure</div><h2>Ideal peaks and finite thickness</h2><a href="Cylinder_Bridge.png"><img src="Cylinder_Bridge.png" alt="Ideal and finite peaks, azimuthal cylinder, mosaic tilts and Ewald-selected scattering"></a><div class="links"><a href="Cylinder_Bridge.pdf">Vector PDF</a><a href="Cylinder_Bridge.svg">Editable SVG</a><a href="Cylinder_Bridge.png">PNG</a><a href="caption.txt">Caption</a></div><p class="caption">CAPTION</p></article>
<footer>Geometric teaching model with declared parameters. Sources, data and verification records are preserved together for reuse.</footer></main></html>'''
    (ROOT/'index.html').write_text(page.replace('CAPTION',caption),encoding='utf-8')

if __name__=='__main__':main()
