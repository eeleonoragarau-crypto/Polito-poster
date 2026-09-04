import asyncio
import json, os
from paths import APP_URL, OUT
from route import handler
from playwright.async_api import async_playwright
async def main():
    logs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1600,'height':1000}, accept_downloads=True)
        pg=await ctx.new_page()
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**','**://api.fontshare.com/**']:
            await pg.route(u, handler)
        pg.on('pageerror', lambda e: logs.append("PAGEERROR: "+str(e)[:300]))
        pg.on('console', lambda m: logs.append(m.type+": "+m.text[:200]) if m.type in ('error',) else None)
        await pg.goto(APP_URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=40000)
        await pg.wait_for_timeout(1800)

        # 1. add clips of every effect on title + para, verify no errors
        res=await pg.evaluate("""async ()=>{
          const out={ok:[],fail:[]};
          for(const [k,f] of Object.entries(FX)){
            for(const t of (f.split?['title','para','claim']:['title','rule','foot'])){
              try{
                const V=curV(); V.clips=[mkClip(t,k,{start:0.2})];
                buildTimeline(false); seekFrame(20); seekFrame(0); seekFrame(60);
                const has=ctxs[t]?1:0;
                out.ok.push(k+'@'+t+(has?'':' (noctx)'));
              }catch(e){ out.fail.push(k+'@'+t+': '+e.message); }
            }
          }
          return out;
        }""")
        print("EFFECTS ok:",len(res['ok']),"fail:",len(res['fail']))
        for f in res['fail']: print("  FAIL",f)

        # restore default + test history
        await pg.evaluate("state=defaultState(); history=[];hIdx=-1;commit('reset');fullRefresh();")
        await pg.wait_for_timeout(800)
        h=await pg.evaluate("""()=>{
          const before=curV().clips.length;
          addClip('para','chars.maskY');
          const after=curV().clips.length;
          undo();
          const undone=curV().clips.length;
          redo();
          const redone=curV().clips.length;
          return {before,after,undone,redone,hist:history.length,hIdx};
        }""")
        print("HISTORY:",h)

        # presets
        pr=await pg.evaluate("""()=>{
          document.querySelector('#presetName').value='test preset';
          savePreset();
          const n=getPresets().length;
          const nm=getPresets()[0].name;
          return {n,nm,ls:!!localStorage.getItem('poliTextLab.presets.v2')};
        }""")
        print("PRESETS:",pr)

        # export single frame webp
        await pg.evaluate("state.export.frame=60; state.export.scale=1; syncPanelInputs();")
        async with pg.expect_download(timeout=90000) as dl:
            await pg.evaluate("exportFrame()")
        d=await dl.value
        path=str(OUT/('exp_'+d.suggested_filename))
        await d.save_as(path)
        print("EXPORT:", d.suggested_filename, os.path.getsize(path),"bytes")

        # sequence zip (small)
        await pg.evaluate("state.export.seqFrom=30;state.export.seqTo=36;state.export.seqStep=3;syncPanelInputs();")
        async with pg.expect_download(timeout=120000) as dl2:
            await pg.evaluate("exportSequence()")
        d2=await dl2.value
        p2=str(OUT/d2.suggested_filename)
        await d2.save_as(p2)
        print("SEQ:", d2.suggested_filename, os.path.getsize(p2),"bytes")

        # clip drag simulation via pointer
        box=await pg.locator('#tracks .clip').first.bounding_box()
        await pg.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2)
        await pg.mouse.down()
        await pg.mouse.move(box['x']+box['width']/2+120, box['y']+box['height']/2, steps=8)
        await pg.mouse.up()
        await pg.wait_for_timeout(500)
        drag=await pg.evaluate("()=>({start:curV().clips.find(c=>c.target==='title').start, hist:history[hIdx].label})")
        print("DRAG:",drag)
        print("LOGS:", logs[-12:])
        await pg.screenshot(path=str(OUT/'shot_final.png'))
        await b.close()
asyncio.run(main())
