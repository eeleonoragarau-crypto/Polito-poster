import asyncio, os
from route import handler
from playwright.async_api import async_playwright
from paths import APP_URL as URL, OUT
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1600,'height':1000}, accept_downloads=True)
        pg=await ctx.new_page()
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        await pg.goto(URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2000)
        await pg.evaluate("""()=>{state.activeVariant=state.variants.findIndex(v=>v.id==='navybeige');
          state.export.scale=1; state.export.frame=Math.round(3.62*30); fullRefresh(); syncPanelInputs();
          document.querySelectorAll('.sec').forEach(d=>d.open=true);}""")
        await pg.wait_for_timeout(700)
        n=await pg.evaluate("()=>{master.time(3.62,true); return document.querySelector('.wipe-layer [data-t=title]').textContent.trim();}")
        print('a schermo:', n)
        async with pg.expect_download(timeout=120000) as d:
            await pg.click('#btnExpFrame')
        f=await d.value; await f.save_as(str(OUT/'exp_mid_count.webp'))
        print('esportato:', f.suggested_filename, os.path.getsize('exp_mid_count.webp'),'byte')
        await b.close()
asyncio.run(main())
