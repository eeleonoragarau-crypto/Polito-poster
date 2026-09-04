import asyncio, json
from route import handler
from playwright.async_api import async_playwright
from paths import APP_URL as URL, OUT
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1600,'height':1000})
        pg=await ctx.new_page()
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        await pg.goto(URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2200)
        r=await pg.evaluate("""()=>{const i=state.variants.findIndex(v=>v.id==='navybeige');
          state.activeVariant=i; state.guides=false; syncGuides(); fullRefresh(); master.time(5.5,true);
          const st=document.querySelector('#stage').getBoundingClientRect();
          const z=st.width/state.format.w;   // fattore di scala a schermo
          const L=sel=>{const e=document.querySelector(sel); if(!e) return null;
            return +(((e.getBoundingClientRect().left-st.left)/z).toFixed(1));};
          return {padNavy:state.variants[i].layout.pad, padBeige:state.variants.find(v=>v.id==='beige').layout.pad,
            titoloBeige:L('.wipe-layer [data-t=title]'), paraBeige:L('.wipe-layer [data-t=para]'),
            footerBeige:L('.wipe-layer [data-t=foot]'), footerNavy:L('#poster [data-t=foot]'),
            attesoPx:+(1080*state.variants[i].layout.pad/100).toFixed(1)};}""")
        print(json.dumps(r, indent=1))
        await pg.locator('#stage').screenshot(path=str(OUT/'nb_end.png'))
        await pg.evaluate("()=>{master.time(3.45,true);}")
        await pg.wait_for_timeout(150)
        await pg.locator('#stage').screenshot(path=str(OUT/'nb_mid.png'))
        await b.close()
asyncio.run(main())
