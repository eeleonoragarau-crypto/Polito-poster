import asyncio, json
from route import handler
from playwright.async_api import async_playwright
from paths import APP_URL as URL, OUT
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1600,'height':1000})
        pg=await ctx.new_page()
        errs=[]; pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        await pg.goto(URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2200)
        r=await pg.evaluate("""()=>{state.activeVariant=state.variants.findIndex(v=>v.id==='navybeige');
          state.guides=true; syncGuides(); fullRefresh();
          const wc=wipeClipOf();
          const labs=[...document.querySelectorAll('#layoutBody .row label')].map(e=>e.textContent.trim());
          return {rev:state.defaultsRev, ovr:Object.fromEntries(OVR_KEYS.map(k=>[k,wc[k]])),
            controlliLayout:labs, guide:document.querySelectorAll('#safeGuides i').length};}""")
        print('pannello:', json.dumps(r, ensure_ascii=False, indent=1))
        # muovo il margin top dal pannello e verifico che il beige si sposti
        m=await pg.evaluate("""()=>{const wc=wipeClipOf(); const out={};
          const misura=()=>{const st=document.querySelector('#stage').getBoundingClientRect();
            const z=st.width/state.format.w;
            const t=document.querySelector('.wipe-layer [data-t=title]').getBoundingClientRect();
            const pa=document.querySelector('.wipe-layer [data-t=para]').getBoundingClientRect();
            return {titoloTop:Math.round((t.top-st.top)/z), titoloLeft:Math.round((t.left-st.left)/z),
                    paraTop:Math.round((pa.top-st.top)/z)};};
          master.time(5.5,true); out.prima=misura();
          wc.ovrTitleTop=6.5; wc.ovrPad=18; wc.ovrParaTop=55; buildTimeline(true); master.time(5.5,true);
          out.dopo=misura();
          out.atteso={titoloTop:Math.round(1350*6.5/100), titoloLeft:Math.round(1080*18/100), paraTop:Math.round(1350*55/100)};
          return out;}""")
        print('spostamento:', json.dumps(m, ensure_ascii=False))
        # bottone "allinea a chi esce"
        al=await pg.evaluate("""()=>{const btns=[...document.querySelectorAll('#layoutBody button')];
          const b=btns.find(x=>/Allinea a chi esce/.test(x.textContent)); b.click();
          const wc=wipeClipOf(); return {pad:wc.ovrPad, titleTop:wc.ovrTitleTop,
            padNavy:curV().layout.pad, topNavy:curV().layout.titleTop};}""")
        print('allinea:', json.dumps(al))
        print('errori:', errs[:5] if errs else 'nessuno')
        await b.close()
asyncio.run(main())
