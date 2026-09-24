const fs=require('node:fs'),path=require('node:path'),{pathToFileURL,fileURLToPath}=require('node:url');
const {chromium}=require('C:/Users/Kenpo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),lib=path.join(root,'presentation_asset_library'),out=path.join(lib,'releases/2026-09-11_v10/provenance');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Kenpo/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe'});
 const errors=[],remote=[],layouts=[];
 const page=await browser.newPage({viewport:{width:1100,height:900}});
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(['error','warning'].includes(m.type()))errors.push(m.text())});
 page.on('request',r=>{if(/^https?:/.test(r.url()))remote.push(r.url())});
 await page.goto(pathToFileURL(path.join(lib,'index.html')).href,{waitUntil:'load'});
 const presentation=await page.locator('.deck-meta').innerText();
 await page.locator('[data-filter=all]').click();
 const totals=await page.evaluate(()=>({assets:document.querySelectorAll('.asset-card').length,slides:document.querySelectorAll('.slide-card').length}));
 if(totals.assets!==32||totals.slides!==26)throw Error(JSON.stringify(totals));
 const links=await page.locator('[href],[src],[poster]').evaluateAll(ns=>ns.flatMap(n=>['href','src','poster'].filter(k=>n.hasAttribute(k)).map(k=>n.getAttribute(k))));
 const missing=[];let checked=0;
 for(const l of [...new Set(links)]){
   if(l.startsWith('#')||l.startsWith('data:'))continue;
   const u=new URL(l,pathToFileURL(path.join(lib,'index.html')));if(u.protocol!=='file:'){missing.push(l);continue}
   if(!fs.existsSync(fileURLToPath(u)))missing.push(l);checked++;
 }
 // Real DOM interactions exercise filters, source disclosure and slide navigation.
 await page.locator('[data-filter=animations]').click();
 if(await page.locator('.asset-card:visible').count()!==16)throw Error('Animation filter count');
 await page.locator('#asset-search').fill('cylinder');
 if(await page.locator('.asset-card:visible').count()!==1)throw Error('Cylinder search count');
 await page.locator('#asset-cylinder-bridge summary').click();
 await page.locator('#asset-cylinder-bridge .slide-jump').click();
 if(await page.locator('#slide-19').getAttribute('hidden')!==null)throw Error('Slide target hidden');
 const slideTitle=await page.locator('#slide-19 h3').innerText();
 if(!slideTitle.includes('From Bragg peaks to diffraction cylinders'))throw Error(slideTitle);
 await page.locator('#slide-19 .asset-jump').click();
 await page.locator('#asset-search').fill('cylinder');
 const video=page.locator('#asset-cylinder-bridge video');
 const metadata=await video.evaluate(async v=>{v.load();await new Promise((resolve,reject)=>{v.addEventListener('loadedmetadata',resolve,{once:true});v.addEventListener('error',()=>reject(Error('Media error')),{once:true})});return {duration:v.duration,width:v.videoWidth,height:v.videoHeight}});
 const seek=[];
 for(const time of [0.5,6.8,11.9,16.5,25]){
   seek.push(await video.evaluate(async(v,t)=>{v.currentTime=t;await new Promise(r=>v.addEventListener('seeked',r,{once:true}));return {requested:t,current:v.currentTime,ready:v.readyState}},time));
 }
 const playback=await video.evaluate(async v=>{v.currentTime=1;await new Promise(r=>v.addEventListener('seeked',r,{once:true}));await v.play();await new Promise(r=>setTimeout(r,500));v.pause();return {advanced:v.currentTime>1.1,current:v.currentTime,error:v.error}});
 if(metadata.duration!==26||metadata.width!==1600||!playback.advanced)throw Error('Movie check');
 for(const width of [1100,390]){
   await page.setViewportSize({width,height:900});
   await page.locator('#asset-cylinder-bridge').scrollIntoViewIfNeeded();
   layouts.push(await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,noOverflow:document.documentElement.scrollWidth<=innerWidth})));
   await page.locator('#asset-cylinder-bridge').screenshot({path:path.join(out,`cylinder_gallery_${width}.png`)});
 }
 await page.locator('[data-filter=all]').click();await page.locator('#asset-search').fill('');
 await page.locator('img').evaluateAll(ns=>ns.forEach(n=>n.loading='eager'));
 await page.waitForFunction(()=>[...document.images].every(i=>i.complete));
 const images=await page.locator('img').evaluateAll(ns=>({count:ns.length,failed:ns.filter(n=>!n.naturalWidth).map(n=>n.src)}));
 const result={ok:errors.length===0&&remote.length===0&&missing.length===0&&images.failed.length===0&&layouts.every(l=>l.noOverflow),presentation,totals,slide19:slideTitle,local_links_checked:checked,missing_links:missing,images,media_metadata:metadata,seek_checks:seek,playback,layouts,console_errors_or_warnings:errors,remote_requests:remote,browser:'isolated Playwright Chromium 1217, headless',scope:'Offline library, source disclosure, search/filter and slide navigation, cylinder playback. Native PowerPoint playback is not tested.'};
 fs.writeFileSync(path.join(out,'gallery_review.json'),JSON.stringify(result,null,2)+'\n');
 await browser.close();console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
