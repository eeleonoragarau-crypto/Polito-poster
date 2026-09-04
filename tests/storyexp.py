import asyncio, json
from route import handler
from playwright.async_api import async_playwright
from paths import APP_URL as URL, OUT
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1600,'height':1000}, accept_downloads=True)
        pg=await ctx.new_page()
        errs=[]; pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        await pg.goto(URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>{state.activeVariant=5; state.export.scale=1; fullRefresh(); syncPanelInputs();}")
        await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{document.querySelectorAll('.sec').forEach(d=>d.open=true);}")
        for t,name in [(3.30,'meta-transizione'),(5.90,'finale')]:
            await pg.evaluate("t=>{state.export.frame=Math.round(t*state.fps); syncPanelInputs();}", t)
            async with pg.expect_download(timeout=120000) as d:
                await pg.click('#btnExpFrame')
            f=await d.value; path=await f.path()
            await f.save_as(str(OUT/('exp_'+name+'.webp')))
            import os
            print('%-16s %-46s %d byte' % (name, f.suggested_filename, os.path.getsize(path)))
        # sequenza zip sulla storia
        await pg.evaluate("()=>{state.export.seqFrom=90;state.export.seqTo=102;state.export.seqStep=3;state.export.type='png';syncPanelInputs();}")
        async with pg.expect_download(timeout=180000) as d2:
            await pg.click('#btnExpSeq')
        f2=await d2.value
        import os
        print('sequenza        %-46s %d byte' % (f2.suggested_filename, os.path.getsize(await f2.path())))
        print('errori:', errs[:6] if errs else 'nessuno')
        await b.close()
asyncio.run(main())
