import asyncio
import json
from paths import APP_URL
from route import handler
from playwright.async_api import async_playwright
OLD = json.dumps({"version":4,"defaultsRev":None,"fps":30,"duration":6,
 "format":{"w":1080,"h":1350,"name":"4:5 · 1080×1350"},"activeVariant":0,"hoverLive":True,"loop":True,"grain":0.05,
 "export":{"scale":2,"quality":0.92,"type":"webp","frame":0,"seqFrom":0,"seqTo":60,"seqStep":2},
 "variants":[{"id":"purple","name":"Purple",
   "colors":{"bg":"#96739c","ink":"#000000","acc":"#111111","logo":"#00284b"},
   "texts":{"title":"WHAT IF\nMY JOB DOESN'T\nEXIST YET?","para":"We give you the tools\nto find your answer.","claim":"Costruiamo\nil tuo futuro."},
   "show":{"para":True,"rule":True,"logo":True,"claim":True},
   "type":{"titleFont":"Bebas Neue","titleWeight":400,"titleSize":14,"titleLh":0.95,"titleTrack":-1.4,"titleCase":"uppercase",
           "bodyFont":"Satoshi","bodyWeight":400,"bodySize":4.2,"bodyLh":1.42,"bodyTrack":-0.5,"claimSize":5},
   "layout":{"pad":9.2,"titleTop":8.5,"titleW":82,"ruleTop":45,"ruleW":15,"ruleH":1.5,"paraTop":58.5,"paraW":66,"footBottom":4.6,"logoW":40},
   "bg":{"mode":"solid","unicornId":"","dpi":1,"scale":1,"fps":60,"scrim":0},
   "clips":[]}]})
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1400,'height':900})
        pg=await ctx.new_page()
        for u in ['**://cdnjs.cloudflare.com/**','**://cdn.jsdelivr.net/**','**://fonts.googleapis.com/**','**://fonts.gstatic.com/**']:
            await pg.route(u, handler)
        # scrivo una sessione "sua" v4 prima del boot
        await pg.add_init_script("try{localStorage.setItem('poliTextLab.session.v4', %s);localStorage.setItem('poliTextLab.session.v5', %s);}catch(e){}" % (json.dumps(OLD), json.dumps(OLD)))
        await pg.goto(APP_URL, wait_until='domcontentloaded')
        await pg.wait_for_selector('#boot', state='detached', timeout=45000)
        await pg.wait_for_timeout(2200)
        r=await pg.evaluate("""()=>{const v=state.variants[0];const cs=getComputedStyle;
          const q=s=>document.querySelector('#poster '+s);
          return {rev:state.defaultsRev, logo:v.colors.logo, bodyWeight:v.type.bodyWeight,
            paraWeightReale:cs(q('[data-t=para]')).fontWeight,
            claimColor:cs(q('[data-t=claim]')).color, dividerColor:cs(q('.p-fdiv')).backgroundColor,
            clips:v.clips.length};}""")
        print('CON SESSIONE VECCHIA v4/v5 GIA PRESENTE:'); print(json.dumps(r,indent=1))
        await b.close()
asyncio.run(main())
