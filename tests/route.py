import os
from paths import NODE
MAP={
 'gsap/3.13.0/gsap.min.js':str(NODE/'gsap/dist/gsap.min.js'),
 'gsap/3.13.0/SplitText.min.js':str(NODE/'gsap/dist/SplitText.min.js'),
 'gsap/3.13.0/ScrambleTextPlugin.min.js':str(NODE/'gsap/dist/ScrambleTextPlugin.min.js'),
 'html2canvas/1.4.1/html2canvas.min.js':str(NODE/'html2canvas/dist/html2canvas.min.js'),
 'jszip/3.10.1/jszip.min.js':str(NODE/'jszip/dist/jszip.min.js'),
}
async def handler(route):
    u=route.request.url
    for k,v in MAP.items():
        if k in u and os.path.exists(v):
            return await route.fulfill(status=200, content_type='application/javascript', body=open(v,'rb').read())
    if 'fontshare' in u:
        return await route.fulfill(status=200, content_type='text/css', body=b'''
@font-face{font-family:'Satoshi';src:url(https://fonts.gstatic.com/local/satoshi.woff2) format('woff2');font-weight:300 900;font-display:block}
''')
    if 'fonts.googleapis' in u:
        css=b'''
@font-face{font-family:'Anton';src:url(https://fonts.gstatic.com/local/anton.woff2) format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Bebas Neue';src:url(https://fonts.gstatic.com/local/bebas.woff2) format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Poppins';src:url(https://fonts.gstatic.com/local/poppins.woff2) format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Inter';src:url(https://fonts.gstatic.com/local/poppins.woff2) format('woff2');font-weight:300 800;font-display:block}
@font-face{font-family:'JetBrains Mono';src:url(https://fonts.gstatic.com/local/poppins.woff2) format('woff2');font-weight:400 700;font-display:block}
'''
        return await route.fulfill(status=200, content_type='text/css', body=css)
    if 'gstatic' in u:
        if 'anton' in u: f=str(NODE/'@fontsource/anton/files/anton-latin-400-normal.woff2')
        elif 'bebas' in u: f=str(NODE/'@fontsource/bebas-neue/files/bebas-neue-latin-400-normal.woff2')
        else: f=str(NODE/'@fontsource/poppins/files/poppins-latin-400-normal.woff2')
        return await route.fulfill(status=200, content_type='font/woff2', body=open(f,'rb').read())
    await route.abort()
