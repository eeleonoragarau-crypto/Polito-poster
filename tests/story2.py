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
        r=await pg.evaluate("""()=>{const i=state.variants.findIndex(v=>v.id==='navybeige');
          state.activeVariant=i; fullRefresh();
          return {rev:state.defaultsRev, tracks:TARGET_ORDER.length,
                  clips:curV().clips.map(c=>[c.target,c.effect,c.start,c.dur]),
                  layer:!!lastWipe(), wt:!!wipeEl('title'), wp:!!wipeEl('para')};}""")
        print('setup:', json.dumps(r, ensure_ascii=False))
        rows=[]
        for t in [0.0,2.9,3.1,3.4,3.8,4.3,4.7,5.5]:
            x=await pg.evaluate("""t=>{master.time(t,true);
              const st=document.querySelector('#stage').getBoundingClientRect();
              const wt=document.querySelector('.wipe-layer [data-t=title]');
              const wp=document.querySelectorAll('.wipe-layer [data-t=para] .stx-line');
              const lg=document.querySelector('.wipe-layer .p-logo');
              const pl=document.querySelector('#poster .p-logo');
              const wl=document.querySelector('.wipe-layer');
              return {t, num:wt?wt.textContent.trim().replace(/\\s+/g,' '):null,
                wipeW:wl?getComputedStyle(wl).width:'-',
                paraLines:wp.length, paraY:wp.length?Math.round(wp[0].getBoundingClientRect().top-st.top):null,
                logoDx:lg?+(lg.getBoundingClientRect().left-pl.getBoundingClientRect().left).toFixed(1):null};}""", t)
            rows.append(x)
        for x in rows: print(json.dumps(x, ensure_ascii=False))
        # override del layout in arrivo
        ov=await pg.evaluate("""()=>{const w=curV().clips.find(c=>c.effect==='wipe.color');
          w.ovrOn=true; seedOvr(w); const seeded=JSON.stringify({pad:w.ovrPad,tt:w.ovrTitleTop,ts:w.ovrTitleSize});
          w.ovrTitleTop=8; w.ovrTitleSize=24; w.ovrPad=16; buildTimeline(true); master.time(5.5,true);
          const st=document.querySelector('#stage').getBoundingClientRect();
          const t=document.querySelector('.wipe-layer [data-t=title]').getBoundingClientRect();
          return {seeded, titoloTop:Math.round(t.top-st.top), titoloLeft:Math.round(t.left-st.left)};}""")
        print('override:', json.dumps(ov, ensure_ascii=False))
        print('errori:', errs[:6] if errs else 'nessuno')
        await b.close()
asyncio.run(main())
