#!/usr/bin/env python3
"""안속템 자료실 빌더: content/posts/*.md → posts/<slug>/index.html, index.html, sitemap.xml

사용: pip install markdown && python3 build.py
글 머리(front matter): title, date(YYYY-MM-DD), slug(영문), summary, insta(연결된 인스타 게시물 제목, 선택)
"""
import pathlib, re, html, datetime
import markdown

SITE = "https://keyfream7001.github.io/ansok-tem"
NAME = "안속템"
INSTA = "https://www.instagram.com/ansok.tem/"
ROOT = pathlib.Path(__file__).parent
AVATAR = "assets/avatar.jpg"

CSS = """
:root{--y:#FF5A36;--k:#111;--g:#666;--line:#eee}
*{box-sizing:border-box}
body{margin:0;font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;color:#1a1a1a;background:#fff;line-height:1.75;word-break:keep-all}
a{color:inherit}
header{background:var(--k);color:#fff}
.bar{max-width:760px;margin:0 auto;padding:16px 20px;display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;font-weight:800;font-size:18px}
.brand img{width:40px;height:40px;border-radius:50%;border:2px solid var(--y)}
.brand small{display:block;font-weight:500;font-size:12px;opacity:.7}
.follow{background:var(--y);color:#111;text-decoration:none;font-weight:800;font-size:14px;padding:8px 14px;border-radius:999px}
main{max-width:760px;margin:0 auto;padding:40px 20px 80px}
h1{font-size:34px;line-height:1.3;letter-spacing:-.5px;margin:0 0 12px}
.meta{color:var(--g);font-size:14px;margin-bottom:28px}
.lead{font-size:18px;color:#333}
h2{font-size:24px;margin:48px 0 12px;padding-top:8px;border-top:3px solid var(--k)}
table{width:100%;border-collapse:collapse;font-size:15px;margin:16px 0;display:block;overflow-x:auto}
th,td{border-bottom:1px solid var(--line);padding:10px 8px;text-align:left;vertical-align:top}
th{background:#fff1ec;font-weight:700;white-space:nowrap}
ul,ol{padding-left:22px}li{margin:6px 0}
li.task{list-style:none;margin-left:-22px}
li.task input{margin-right:8px;transform:scale(1.2)}
blockquote,.note{background:#fff1ec;border-radius:12px;padding:14px 18px;margin:20px 0}
.cta{margin-top:56px;background:var(--k);color:#fff;border-radius:16px;padding:28px 24px;display:flex;gap:18px;align-items:center}
.cta img{width:64px;height:64px;border-radius:50%;border:3px solid var(--y);flex-shrink:0}
.cta b{color:var(--y)}
.cta a{display:inline-block;margin-top:10px;background:var(--y);color:#111;text-decoration:none;font-weight:800;padding:8px 16px;border-radius:999px}
.cards{list-style:none;padding:0;margin:0;display:grid;gap:14px}
.cards li{border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.cards a{text-decoration:none}
.cards h3{margin:0 0 6px;font-size:20px}
.cards p{margin:0;color:#555;font-size:15px}
.cards time{color:var(--g);font-size:13px}
.hero{background:var(--k);color:#fff;border-radius:18px;padding:32px 26px;margin-bottom:36px}
.hero h1 span{color:var(--y)}
.hero p{color:#ccc;margin:0}
footer{border-top:1px solid var(--line);color:var(--g);font-size:13px;text-align:center;padding:28px 20px}
"""

def page(title, desc, body, url, og_type="website"):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{AVATAR}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style>
<!-- AdSense 승인 후 여기에 스크립트 추가 -->
</head>
<body>
<header><div class="bar">
<a class="brand" href="{SITE}/"><img src="{SITE}/{AVATAR}" alt=""><span>{NAME}<small>상세페이지에 안 속는 살림템</small></span></a>
<a class="follow" href="{INSTA}">인스타 팔로우</a>
</div></header>
<main>
{body}
</main>
<footer>© {datetime.date.today().year} {NAME} · <a href="{INSTA}">@ansok.tem</a> · <a href="{SITE}/privacy/">개인정보처리방침</a> · 이 사이트의 일부 링크는 쿠팡파트너스 링크로, 구매 시 일정액의 수수료를 받습니다. 가격은 게시 시점 기준입니다.</footer>
</body>
</html>
"""

def parse(p):
    raw = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    meta = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    return meta, m.group(2).strip()

def to_html(md):
    out = markdown.markdown(md, extensions=["tables"])
    out = re.sub(r"<li>\[ \]\s*", '<li class="task"><input type="checkbox" aria-label="체크"> ', out)
    out = re.sub(r"<li>\[x\]\s*", '<li class="task"><input type="checkbox" checked aria-label="체크"> ', out)
    out = out.replace("<p><em>", '<p class="note"><em>', 1) if "<p><em>" in out else out
    return out

CTA = f"""<div class="cta"><img src="{SITE}/{AVATAR}" alt="">
<div>제품사진 6년 찍은 사람이 <b>상세페이지에 안 속는 살림템</b>을 골라요.<br>인스타 게시물에 댓글을 남기면 상품 링크를 DM으로 보내드려요.<br>
<a href="{INSTA}">@ansok.tem 팔로우하기</a></div></div>"""

def main():
    posts = []
    for p in sorted((ROOT / "content/posts").glob("*.md")):
        meta, md = parse(p)
        slug = meta["slug"]; url = f"{SITE}/posts/{slug}/"
        body_html = to_html(md)
        insta = f' · 인스타 「{html.escape(meta["insta"])}」 자료' if meta.get("insta") else ""
        body = f'<article><h1>{html.escape(meta["title"])}</h1><div class="meta"><time datetime="{meta["date"]}">{meta["date"]}</time>{insta}</div>{body_html}</article>{CTA}'
        d = ROOT / "posts" / slug; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(f'{meta["title"]} | {NAME}', meta.get("summary", ""), body, url, "article"), encoding="utf-8")
        posts.append((meta, url))
    posts.sort(key=lambda x: x[0]["date"], reverse=True)
    items = "".join(f'<li><a href="{u}"><time>{m["date"]}</time><h3>{html.escape(m["title"])}</h3><p>{html.escape(m.get("summary",""))}</p></a></li>' for m, u in posts)
    home = f"""<section class="hero"><h1>{NAME} <span>자료실</span></h1><p>6년째 혼자 사업하는 사장의 돈·일 노트입니다. 인스타그램 카드뉴스에서 약속한 정리본이 여기에 쌓여요.</p></section>
<ul class="cards">{items}</ul>{CTA}"""
    (ROOT / "index.html").write_text(page(f"{NAME} 자료실 | 상세페이지에 안 속는 살림템", "6년째 혼자 사업하는 사장의 돈·일 노트. 체크리스트와 템플릿 자료실.", home, f"{SITE}/"), encoding="utf-8")
    urls = [f"{SITE}/"] + [u for _, u in posts]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"built {len(posts)} posts")

if __name__ == "__main__":
    main()
