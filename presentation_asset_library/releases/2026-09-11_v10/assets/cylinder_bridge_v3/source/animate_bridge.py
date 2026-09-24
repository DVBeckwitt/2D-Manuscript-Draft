"""Render the cylinder bridge as a 16:9, H.264 animation from shared geometry."""
from pathlib import Path
import argparse
import hashlib
import inspect
import json
import os
import shutil
import subprocess
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import cylinder_bridge as cb

ROOT=Path(__file__).resolve().parents[1]
DURATION=26.0
BOUNDARIES=[0.0,8.0,12.2,17.0,26.0]
LABELS=['Bragg peaks to rod','Azimuthal average','Mosaic tilts','Ewald selection']
TITLES=['One reciprocal\nrod','Random in-plane\norientations','A distribution\nof normal tilts','Intensity selected\non the Ewald sphere']
SUBTITLES=['Finite stacking gives\nintensity along L.',
           'The rod sweeps out\na hollow cylinder.',
           'Rotate the same rod\nintensity with each normal.',
           'A narrow intersection\nbecomes a weighted patch.']
INK='#233442';TEAL='#087F8C';GREY='#71818B'

def ease(x):
    x=np.clip(x,0,1)
    return float(x*x*(3-2*x))

def state(t):
    # Accelerate the visible peak-width progression; no final slow-down.
    if t<8.0:return 0,float(np.clip((t-1.0)/5.8,0,1))**2
    if t<12.2:return 1,ease((t-8.0)/3.3)
    if t<17.0:return 2,ease((t-12.2)/3.6)
    return 3,ease((t-17.0)/4.0)

def render_frame(t,width=1600,height=900):
    stage,progress=state(t)
    fig=plt.figure(figsize=(width/100,height/100),dpi=100,facecolor='white')
    fig.text(.05,.938,'From Bragg peaks to diffraction cylinders',color=INK,
             fontsize=26,fontweight='bold',ha='left')
    for i,label in enumerate(LABELS):
        x=.054+i*.235
        color=TEAL if i==stage else '#A4AFB6'
        fig.add_artist(Ellipse((x+.006,.857),24/width,24/height,transform=fig.transFigure,
                               facecolor=color,edgecolor='none'))
        fig.text(x+.006,.857,str(i+1),fontsize=9,color='white',ha='center',va='center',fontweight='bold')
        fig.text(x+.025,.856,label,fontsize=13.8,color=color,va='center',fontweight='bold' if i==stage else 'normal')
    ax=fig.add_axes([.295,.155,.675,.646])
    cb.draw_stage(ax,stage,progress=progress,annotations=False,fontsize=14)
    # Same camera angle; expand the viewport smoothly as the larger sphere enters.
    zoom=progress if stage==3 else 0.0
    ax.set_ylim(-.55+zoom*(-1.75+.55),4.55+zoom*(5.46-4.55))
    title,subtitle=TITLES[stage],SUBTITLES[stage]
    if stage==0:
        if progress==0:
            title='Near-ideal Bragg\npeaks'
            subtitle='A very thick crystal:\npeaks appear delta-like.'
        else:
            title='Finite thickness\nbroadens the peaks'
            subtitle='A thinner stack gives\nwider peaks and fringes.'
    fig.text(.051,.637,title,fontsize=25,color=INK,fontweight='bold',va='top',linespacing=1.25)
    fig.text(.054,.472,subtitle,fontsize=17,color=GREY,va='top',linespacing=1.5)
    if t>=22:
        fig.text(.054,.225,'Next: stacking changes\nintensity along these rods.',fontsize=16.5,
                 color=TEAL,fontweight='bold',linespacing=1.5,va='top')
    fig.text(.052,.062,'Geometric illustration  ·  ordered stack  ·  fixed wavelength',
             color=GREY,fontsize=11.5)
    fig.text(.948,.062,f'{stage+1} / 4',color=GREY,fontsize=11.5,ha='right')
    fig.canvas.draw()
    rgb=np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()
    plt.close(fig)
    return rgb

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--movie',action='store_true')
    parser.add_argument('--proofs',action='store_true')
    parser.add_argument('--width',type=int,default=1600)
    parser.add_argument('--height',type=int,default=900)
    parser.add_argument('--fps',type=int,default=20)
    parser.add_argument('--full-render',action='store_true',
        help='Render all later geometry instead of reusing the bundled unchanged v2 movie tail.')
    args=parser.parse_args()
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'axes.labelcolor':INK,
                         'font.size':9,'savefig.facecolor':'white'})
    ROOT.mkdir(parents=True,exist_ok=True)
    if args.proofs or not args.movie:
        from PIL import Image
        p=ROOT/'storyboard';p.mkdir(exist_ok=True)
        for t in [0.0,1.0,1.2,2.0,3.5,5.0,6.0,6.8,7.5,9.5,11.9,14.0,16.5,19.0,21.5,25.0]:
            filename=f'frame_{t:04.1f}s.png'
            Image.fromarray(render_frame(t,args.width,args.height)).save(p/filename)
            print('PROOF '+filename,flush=True)
        shutil.copyfile(p/'frame_25.0s.png',ROOT/'Cylinder_Bridge_poster.png')
    if args.movie:
        ffmpeg=os.environ.get('FFMPEG_BIN') or shutil.which('ffmpeg')
        if not ffmpeg and Path('C:/ffmpeg/bin/ffmpeg.exe').exists():ffmpeg='C:/ffmpeg/bin/ffmpeg.exe'
        if not ffmpeg:raise RuntimeError('Install FFmpeg or set FFMPEG_BIN to its executable.')
        path=ROOT/'Cylinder_Bridge.mp4'
        command=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo',
                 '-pix_fmt','rgb24','-s',f'{args.width}x{args.height}','-r',str(args.fps),'-i','-',
                 '-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
                 '-movflags','+faststart',str(path)]
        proc=subprocess.Popen(command,stdin=subprocess.PIPE)
        frames=round(DURATION*args.fps);start=time.time()
        # Static holds repeat exactly. Reuse their pixels rather than rebuilding
        # hundreds of thousands of identical Ewald segments each frame.
        previous_key=None;previous_rgb=None;rendered=0;reused=0;decoder=None
        retained=ROOT/'data/retained_v2_movie.mp4'
        reuse_tail=not args.full_render and retained.exists()
        if reuse_tail:
            expected='bf4c4829ff110c9f80b4519f07aa40ed2bab3d7483c85be7c1cb23171abcee8a'
            assert hashlib.sha256(retained.read_bytes()).hexdigest()==expected,'Unexpected retained movie'
        try:
            for n in range(frames):
                t=n/args.fps
                if reuse_tail and t>=8:
                    if decoder is None:
                        cmd=[ffmpeg,'-hide_banner','-loglevel','error','-ss','8','-i',str(retained),
                            '-vf',f'scale={args.width}:{args.height},fps={args.fps}',
                            '-an','-f','rawvideo','-pix_fmt','rgb24','-']
                        decoder=subprocess.Popen(cmd,stdout=subprocess.PIPE)
                    rgb=decoder.stdout.read(args.width*args.height*3)
                    if len(rgb)!=args.width*args.height*3:raise RuntimeError('Retained tail ended early')
                    proc.stdin.write(rgb);reused+=1
                    continue
                stage,progress=state(t)
                scene_progress=cb.opening_layer_count(progress) if stage==0 else progress
                key=(stage,scene_progress,t>=22)
                if key!=previous_key:
                    previous_rgb=render_frame(t,args.width,args.height).tobytes()
                    previous_key=key;rendered+=1
                proc.stdin.write(previous_rgb)
                if n%40==0:print(f'FRAME {n}/{frames} elapsed={time.time()-start:.1f}s',flush=True)
        finally:
            proc.stdin.close()
            if decoder is not None:
                decoder.stdout.close()
                if decoder.wait()!=0:raise RuntimeError('Retained tail decode failed')
        if proc.wait()!=0:raise RuntimeError('FFmpeg failed.')
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        report={'file':path.name,'sha256':sha,'duration_seconds':DURATION,'frames':frames,'fps':args.fps,
                'width':args.width,'height':args.height,'codec':'H.264','pixel_format':'yuv420p',
                'audio':False,'timeline_seconds':BOUNDARIES,
                'geometry_source':'source/cylinder_bridge.py','intensity_model':'See shared geometry provenance',
                'opening':'Near-delta N=512 finite peaks followed by a continuous neighboring-integer thickness population down to mean N=8. Peak-normalized display.',
                'continuous_progress':'Actual azimuth sweep and scaled rigid mosaic rotations after the thickness opening; N=8 and source state then remain fixed.',
                'opening_pacing':'Hold 0–1s; inverse mean thickness advances as u² over 1–6.8s; hold final N8 to8s. Visible broadening accelerates.',
                'rendered_scenes':rendered,'identical_hold_frames_reused':frames-rendered-reused,
                'retained_tail_frames':reused,'retained_tail_source':'data/retained_v2_movie.mp4' if reused else None,
                'retained_tail_sha256':hashlib.sha256(retained.read_bytes()).hexdigest() if reused else None,
                'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'matplotlib':matplotlib.__version__,'numpy':np.__version__}
        (ROOT/'provenance').mkdir(exist_ok=True)
        (ROOT/'provenance/animation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('MOVIE '+str(path),flush=True)

if __name__=='__main__':main()
