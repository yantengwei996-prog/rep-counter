"""Build the GitHub Pages site from index.html (the same source the claude.ai artifact uses).
Adds the page head the artifact host normally provides, plus home-screen (PWA) and offline support."""
import os, sys, shutil, json, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

os.makedirs(os.path.join(SITE, "voices"), exist_ok=True)
shutil.copy(os.path.join(ROOT, "voices", "anna.json"), os.path.join(SITE, "voices", "anna.json"))

HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="转动圆环调组数、个数、速度，真人语音报数的运动计数器。">
<meta name="theme-color" content="#282623">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="运动计数器">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" type="image/png" href="icon-192.png">
<style>
html{box-sizing:border-box;background:#282623}
body{margin:0}
[hidden]{display:none!important}
</style>
"""
# Full screen: the page itself runs under the status bar and the home bar (the light field fills them),
# while the content keeps clear of them. Comes after the app's own styles so it wins.
FULLBLEED = """
<style>
html,body{height:100%;min-height:100dvh}
body{background:#282623}
.app{padding-top:calc(env(safe-area-inset-top,0px) + 24px);padding-bottom:calc(env(safe-area-inset-bottom,0px) + 24px)}
.title{top:calc(env(safe-area-inset-top,0px) + 14px)}
/* The very top and bottom of the light field always end in these two colours, whatever the glows are doing.
   Safari tints the area behind its status bar and toolbar from the page edge, so the two now meet without a dark band. */
.field::before{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;
  background:linear-gradient(180deg,#282623 0,rgba(40,38,35,0) 10%,rgba(39,46,43,0) 90%,#272E2B 100%)}
.edge{position:fixed;left:0;right:0;height:2px;z-index:2;pointer-events:none}
.edge.top{top:0;background:#282623}
.edge.bottom{bottom:0;background:#272E2B}
</style>
"""
EDGES = '<div class="edge top" aria-hidden="true"></div><div class="edge bottom" aria-hidden="true"></div>\n'
SW_REG = """
<script>
if ('serviceWorker' in navigator) addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
</script>
"""
# the source starts with <title>, <meta>, <link>s and then <style>; keep those in <head>
i = src.index("<style>")
html = HEAD + src[:i] + src[i:src.index("</style>") + len("</style>")] + FULLBLEED + "\n</head>\n<body>\n" + EDGES + src[src.index("</style>") + len("</style>"):] + SW_REG + "</body>\n</html>\n"
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="\n").write(html)

manifest = {
    "name": "运动计数器", "short_name": "计数器", "lang": "zh-CN",
    "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
    "background_color": "#282623", "theme_color": "#282623",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
}
json.dump(manifest, open(os.path.join(SITE, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# cache version follows the content, so a new deploy replaces the old offline copy
h = hashlib.sha1()
for f in ("index.html", "voices/anna.json"):
    h.update(open(os.path.join(SITE, f), "rb").read())
version = h.hexdigest()[:10]
SW = """// offline support: the page, the voice pack and the fonts are kept on the phone after the first visit
const CACHE = 'rep-counter-%s';
const CORE = ['./', 'index.html', 'voices/anna.json', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-180.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const font = url.host === 'fonts.googleapis.com' || url.host === 'fonts.gstatic.com';
  if (url.origin !== location.origin && !font) return;
  const keep = res => { if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return res; };
  // the page itself: newest version from the network when online (so updates show up at once), cached copy when offline
  if (req.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/')) {
    e.respondWith(fetch(req).then(keep).catch(() => caches.match(req, {ignoreSearch: true}).then(hit => hit || caches.match('index.html'))));
    return;
  }
  // voice pack, icons, fonts: cache first (they only change together with a new cache version)
  e.respondWith(caches.match(req, {ignoreSearch: true}).then(hit => hit || fetch(req).then(keep)));
});
""" % version
open(os.path.join(SITE, "sw.js"), "w", encoding="utf-8", newline="\n").write(SW)

README = """# 运动计数器

转动圆环调整组数、个数、速度，中心点“开始”，真人语音报数。

- 打开网页即可使用；iPhone 用 Safari 打开后点「分享 → 添加到主屏幕」，安卓用 Chrome 菜单里的「添加到主屏幕」。
- 第一次打开后可以离线使用。
- 语音：Anna Su（ElevenLabs eleven_v4 生成）。
"""
open(os.path.join(SITE, "README.md"), "w", encoding="utf-8", newline="\n").write(README)
print("site built, cache version", version)
