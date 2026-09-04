import asyncio
import json
from paths import APP_URL, OUT
from route import handler
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':950})
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:250]))
        pg.on('console', lambda m: errs.append('console '+m.text[:150]) if m.type=='error' else None)
        await pg.goto(APP_URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2600)
        print('codrops effects:', await pg.evaluate("Object.keys(FX).filter(k=>k.startsWith('codrops'))"))
        print('total effects:', await pg.evaluate("Object.keys(FX).length"))
        print('satoshi loaded:', await pg.evaluate("document.fonts.check('400 16px Satoshi')"),
              '| faces:', await pg.evaluate("[...document.fonts].filter(f=>f.family==='Satoshi').map(f=>f.weight+':'+f.status)"))
        for i,name in [(0,'f_purple'),(1,'f_navy'),(2,'f_green'),(3,'f_orange')]:
            await pg.evaluate(f"state.activeVariant={i}; fullRefresh();"); await pg.wait_for_timeout(1200)
            # aggiungo lo scramble codrops e vado a metà effetto: il colore NON deve cambiare
            await pg.evaluate("""(()=>{const V=curV();
              V.clips=V.clips.filter(c=>!c.effect.startsWith('codrops'));
              V.clips.push(mkClip('title','codrops.scramble',{start:2.4,dur:1.2,stagger:.045,cycles:3}));
              V.clips.push(mkClip('para','codrops.scramble',{start:2.4,dur:1.2,stagger:.03,cycles:3}));
              buildTimeline(false);})()""")
            await pg.evaluate("seekFrame(88)"); await pg.wait_for_timeout(350)
            r=await pg.evaluate("""()=>{const cs=getComputedStyle;
              const ch=ctxs.title&&ctxs.title.chars[0], pl=ctxs.para&&ctxs.para.lines[0];
              const st=document.querySelector('#stage');
              return {ink:cs(st).getPropertyValue('--v-ink').trim(),
                titleChar:ch?cs(ch).color:null, para:pl?cs(pl).color:null,
                bars:document.querySelectorAll('#poster i,#poster .cd-bar').length,
                bodyFont:cs(document.querySelector('#poster [data-t=para]')).fontFamily.slice(0,30)};}""")
            print(name, json.dumps(r))
            await pg.locator('#stage').screenshot(path=str(OUT/(name+'.png')))
        print('ERR:', errs[:6])
        await b.close()
asyncio.run(main())
