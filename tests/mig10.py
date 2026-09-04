import asyncio, json
from route import handler
from playwright.async_api import async_playwright
from paths import APP_URL as URL, OUT
async def boot(pg):
    for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
        await pg.route(u, handler)
    await pg.goto(URL, wait_until='domcontentloaded')
    await pg.wait_for_selector('#boot', state='detached', timeout=45000)
    await pg.wait_for_timeout(1900)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1500,'height':950})
        pg=await ctx.new_page(); await boot(pg)
        # simulo il file che ha in mano lui: rev 8, nessun override, tempi spostati a mano
        await pg.evaluate("""()=>{
          state.defaultsRev=8;
          const v=state.variants.find(x=>x.id==='navybeige');
          v.clips.forEach(c=>{ OVR_KEYS.forEach(k=>delete c[k]); delete c.toVarId; });
          const wc=v.clips.find(c=>c.effect==='wipe.color'); wc.start=3.10; wc.dur=1.20;
          const ct=v.clips.find(c=>c.effect==='count.up');   ct.start=3.40; ct.dur=1.80;
          saveSession();}""")
        await pg.wait_for_timeout(300)
        pg2=await ctx.new_page(); await boot(pg2)
        r=await pg2.evaluate("""()=>{const v=state.variants.find(x=>x.id==='navybeige');
          const wc=v.clips.find(c=>c.effect==='wipe.color'), ct=v.clips.find(c=>c.effect==='count.up');
          const dest=destVariant(wc);
          return {rev:state.defaultsRev, arrivo:dest?dest.id:null, toVarId:wc.toVarId,
            tempi:{wipe:[wc.start,wc.dur],counter:[ct.start,ct.dur]},
            ovr:{pad:wc.ovrPad,titleTop:wc.ovrTitleTop,titleSize:wc.ovrTitleSize,paraTop:wc.ovrParaTop}};}""")
        print(json.dumps(r, ensure_ascii=False))
        await b.close()
asyncio.run(main())
