import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=process.cwd(),tmp=path.join(root,'build_codex/slate_talk/animated_deck_v10');
await fs.mkdir(tmp,{recursive:true});
const p=Presentation.create({slideSize:{width:1280,height:720}}),s=p.slides.add();
s.background.fill='#FFFFFF';
s.images.add({blob:new Uint8Array(await fs.readFile(path.join(root,'output/cylinder_bridge_v3/storyboard/frame_00.0s.png'))),
 contentType:'image/png',alt:'Cylinder bridge v3: finite-thickness broadening, azimuthal averaging, mosaic tilt and Ewald selection',
 fit:'contain',position:{left:0,top:0,width:1280,height:720}});
s.speakerNotes.textFrame.setText(`From Bragg peaks to diffraction cylinders

Suggested pace: 30 seconds. Click once to play the 26-second sequence, then advance after its final hold.

A very thick ordered crystal gives narrow Bragg peaks. Finite normal thickness broadens those peaks and produces fringes along reciprocal rods. Random in-plane orientations sweep the rods into cylinders. Different crystal normals rotate those cylinders, and the Ewald sphere selects their scattering. Stacking disorder will change intensity along these existing rods.

Source: Cylinder_Bridge.mp4, cylinder_bridge_v3, created in task codex://threads/01a08bed-6ea7-7721-934d-f260c5ed4faf. Matching static figure and full caption: output/cylinder_bridge_v3/Cylinder_Bridge.pdf and caption.txt.

The smooth opening is an illustrative incoherent population of neighboring integer stack thicknesses, from mean N=512 to N=8, with peak normalization. Faster visible broadening is presentation timing, not an inferred layer-removal rate. The remaining geometry uses the fixed N=8 model. Mosaic and Ewald shading illustrate selected geometric contributions, not calibrated detector counts or fitted sample parameters.`);
await (await PresentationFile.exportPptx(p)).save(path.join(tmp,'bridge_slide.pptx'));
const inspection=await p.inspect({kind:'slide,image,notes,layout',maxChars:12000});
await fs.writeFile(path.join(tmp,'bridge_slide.inspect.ndjson'),inspection.ndjson);
console.log('Created one full-canvas animation poster slide.');
