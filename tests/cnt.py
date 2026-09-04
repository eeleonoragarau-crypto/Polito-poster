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
        await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>{state.activeVariant=4; fullRefresh();}")
        await pg.wait_for_timeout(800)
        out=[]
        for t in [0,0.2,0.6,1.0,1.5,2.0,2.6,3.7,5.0]:
            r=await pg.evaluate("""t=>{master.time(t,true);
              const e=document.querySelector('#poster [data-t=title]');
              return {t, txt:e.textContent.trim().slice(0,24), dur:master.duration()};}""", t)
            out.append(r)
        print(json.dumps(out,indent=0))
        info=await pg.evaluate("""()=>curV().clips.map(c=>[c.target,c.effect,c.start,c.dur])""")
        print('clips:',json.dumps(info))
        await b.close()
asyncio.run(main())
