import asyncio
import json, os
from paths import APP_URL, OUT
from route import handler
from playwright.async_api import async_playwright
async def main():
    logs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1600,'height':1000},accept_downloads=True)
        pg=await ctx.new_page()
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        pg.on('pageerror', lambda e: logs.append("PAGEERROR: "+str(e)[:300]))
        pg.on('console', lambda m: logs.append(m.type+': '+m.text[:200]) if m.type=='error' else None)
        await pg.goto(APP_URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2200)
        print('variants:', await pg.evaluate("state.variants.map(v=>v.id+':'+v.colors.bg+'/'+v.colors.logo)"))
        # orange poster
        await pg.evaluate("state.activeVariant=3; fullRefresh();"); await pg.wait_for_timeout(1300)
        await pg.evaluate("seekFrame(90)"); await pg.wait_for_timeout(400)
        await pg.locator('#stage').screenshot(path=str(OUT/'w_orange.png'))
        # add a wipe clip on each direction and screenshot mid-transition
        res=await pg.evaluate("""()=>{
          const out=[];
          for(const d of ['lr','rl','tb','bt']){
            const V=curV();
            V.clips=V.clips.filter(c=>c.effect!=='wipe.color');
            const c=mkClip('wipe','wipe.color',{start:1.0,dur:1.2,wipeDir:d,toVar:0,parallax:.6,pushOut:.3});
            V.clips.push(c); buildTimeline(false);
            seekFrame(48);
            const L=document.querySelector('.wipe-layer');
            out.push({d, layers:document.querySelectorAll('.wipe-layer').length,
              w:L?L.style.width:null, h:L?L.style.height:null,
              box:L?JSON.stringify(L.getBoundingClientRect().toJSON()).slice(0,90):null});
          }
          return out;
        }""")
        for r in res: print(r)
        # visual: lr mid
        await pg.evaluate("""(()=>{const V=curV();V.clips=V.clips.filter(c=>c.effect!=='wipe.color');
          V.clips.push(mkClip('wipe','wipe.color',{start:1.0,dur:1.4,wipeDir:'lr',toVar:1,parallax:.65,pushOut:.3}));
          buildTimeline(false);})()""")
        for f,name in [(42,'w_lr_a'),(52,'w_lr_b'),(66,'w_lr_c')]:
            await pg.evaluate(f"seekFrame({f})"); await pg.wait_for_timeout(250)
            await pg.locator('#stage').screenshot(path=str(OUT/(name+'.png')))
        # withText variant
        await pg.evaluate("""(()=>{const V=curV();V.clips=V.clips.filter(c=>c.effect!=='wipe.color');
          V.clips.push(mkClip('wipe','wipe.color',{start:1.0,dur:1.4,wipeDir:'rl',toVar:1,parallax:.6,pushOut:.25,withText:true}));
          buildTimeline(false);})()""")
        await pg.evaluate("seekFrame(54)"); await pg.wait_for_timeout(300)
        await pg.locator('#stage').screenshot(path=str(OUT/'w_withtext.png'))
        # chained wipes
        await pg.evaluate("""(()=>{const V=curV();V.clips=V.clips.filter(c=>c.effect!=='wipe.color');
          V.clips.push(mkClip('wipe','wipe.color',{start:0.8,dur:1.0,wipeDir:'lr',toVar:1,parallax:.5,pushOut:.25}));
          V.clips.push(mkClip('wipe','wipe.color',{start:2.2,dur:1.0,wipeDir:'tb',toVar:2,parallax:.5,pushOut:.25}));
          buildTimeline(false);})()""")
        await pg.evaluate("seekFrame(80)"); await pg.wait_for_timeout(300)
        await pg.locator('#stage').screenshot(path=str(OUT/'w_chain.png'))
        print('chain layers:', await pg.evaluate("document.querySelectorAll('.wipe-layer').length"))
        # export mid-wipe
        await pg.evaluate("state.export.frame=80; state.export.scale=1; syncPanelInputs();")
        async with pg.expect_download(timeout=90000) as dl:
            await pg.evaluate("exportFrame()")
        d=await dl.value; path=str(OUT/'exp_wipe.webp'); await d.save_as(path)
        print('EXPORT mid-wipe:', os.path.getsize(path),'bytes')
        print('LOGS:', logs[-10:])
        await b.close()
asyncio.run(main())
