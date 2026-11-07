"""Export only published Notion pages. No API responses or signed URLs are persisted."""
import hashlib
import html
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '75d45a99-5c45-4706-8855-e2255b3011b0'

def esc(s): return html.escape(str(s), quote=True)
def safe_url(url):
    p = urllib.parse.urlsplit(url or '')
    return url if p.scheme in ('https', 'http', 'mailto') else '#'

def rich(items):
    out = ''
    for item in items:
        value = esc(item.get('plain_text', item.get('text', {}).get('content', item.get('equation', {}).get('expression', ''))))
        a = item.get('annotations', {})
        for key, tag in [('code','code'),('bold','strong'),('italic','em'),('strikethrough','s'),('underline','u')]:
            if a.get(key): value = f'<{tag}>{value}</{tag}>'
        url = item.get('href') or (item.get('text', {}).get('link') or {}).get('url')
        if url: value = f'<a href="{esc(safe_url(url))}" rel="noopener noreferrer">{value}</a>'
        out += value
    return out

def text(prop):
    return ''.join(x.get('plain_text', x.get('text', {}).get('content','')) for x in prop.get(prop.get('type','rich_text'), []))

class API:
    def __init__(self): self.token = os.environ['NOTION_TOKEN']
    def request(self, path, payload=None):
        for attempt in range(6):
            req = urllib.request.Request('https://api.notion.com/v1/' + path,
                data=json.dumps(payload).encode() if payload is not None else None,
                headers={'Authorization':'Bearer '+self.token, 'Notion-Version':'2025-09-03','Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=45) as response: return json.load(response)
            except urllib.error.HTTPError as e:
                if e.code not in (429,500,502,503,504) or attempt == 5:
                    raise RuntimeError(f'Notion API failed ({e.code}); check integration access and schema.') from None
                time.sleep(min(30, int(e.headers.get('Retry-After', 2 ** attempt))))
        raise RuntimeError('Notion request exhausted')
    def pages(self):
        payload = {'filter':{'property':'Status','select':{'equals':'published'}}, 'page_size':100}
        while True:
            result = self.request(f'data_sources/{SOURCE}/query', payload)
            yield from result['results']
            if not result.get('has_more'): break
            payload['start_cursor'] = result['next_cursor']
    def blocks(self, parent, depth=0):
        if depth > 20: raise ValueError('Article nesting exceeds 20 levels')
        cursor = ''
        result_blocks = []
        while True:
            result = self.request(f'blocks/{parent}/children?page_size=100'+('&start_cursor='+cursor if cursor else ''))
            for block in result['results']:
                if block.get('has_children'): block['children'] = self.blocks(block['id'], depth+1)
                result_blocks.append(block)
            if not result.get('has_more'): return result_blocks
            cursor = result['next_cursor']

class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_host(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def check_host(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.port not in (None,443): raise ValueError('Image must use public HTTPS')
    addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses): raise ValueError('Image host must be public')

class Images:
    def __init__(self, root): self.root = root
    def save(self, obj):
        if not obj: return ''
        url = obj.get(obj.get('type',''), {}).get('url')
        if not url: raise ValueError('Unsupported image source')
        check_host(url)
        # Never send the Notion Authorization header to an image host.
        try:
            with urllib.request.build_opener(PublicRedirect()).open(url, timeout=45) as response:
                raw = response.read(25*1024*1024+1)
            if len(raw) > 25*1024*1024: raise ValueError('Image exceeds 25 MB')
            with Image.open(io.BytesIO(raw)) as source:
                image = ImageOps.exif_transpose(source).convert('RGB')
                image.thumbnail((2400,2400))
                output = io.BytesIO(); image.save(output, 'WEBP', quality=84, method=6)
            data = output.getvalue()
        except Exception:
            raise RuntimeError('Image download/optimization failed; previous publication retained. Re-upload the image in Notion.') from None
        name = hashlib.sha256(data).hexdigest()[:24]+'.webp'
        dest = self.root/'adventures/images/notion'/name
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        return '/adventures/images/notion/'+name

def render(blocks, images):
    result = ''; list_kind = None
    for block in blocks:
        kind = block['type']; value = block.get(kind,{})
        content = rich(value.get('rich_text', []))
        children = render(block.get('children', []), images)
        tag = {'bulleted_list_item':'ul','numbered_list_item':'ol'}.get(kind)
        if list_kind and list_kind != tag: result += f'</{list_kind}>'; list_kind = None
        if tag:
            if list_kind != tag: result += f'<{tag}>'; list_kind = tag
            result += f'<li>{content}{children}</li>'; continue
        if kind == 'paragraph': result += f'<p>{content}</p>'+children
        elif kind.startswith('heading_'): result += f'<h{int(kind[-1])+1}>{content}</h{int(kind[-1])+1}>'+children
        elif kind == 'image':
            path = images.save(value); caption = rich(value.get('caption', []))
            result += f'<figure><img loading="lazy" src="{esc(path)}" alt="{esc(text({"type":"rich_text","rich_text":value.get("caption",[])}))}"><figcaption>{caption}</figcaption></figure>'
        elif kind in ('quote','callout'): result += f'<blockquote>{content}{children}</blockquote>'
        elif kind == 'toggle': result += f'<details><summary>{content}</summary>{children}</details>'
        elif kind == 'divider': result += '<hr>'
        elif kind == 'code': result += f'<pre><code>{esc(text({"type":"rich_text","rich_text":value.get("rich_text",[])}))}</code></pre>'
        elif kind == 'to_do': result += f'<p>{"☑" if value.get("checked") else "☐"} {content}</p>'+children
        elif kind in ('column_list','column'): result += children
        elif kind == 'table': result += '<div class="table-scroll"><table>'+children+'</table></div>'
        elif kind == 'table_row': result += '<tr>'+''.join('<td>'+rich(c)+'</td>' for c in value['cells'])+'</tr>'
        elif kind in ('bookmark','link_preview'): result += f'<p><a href="{esc(safe_url(value.get("url","")))}">{esc(value.get("url","Link"))}</a></p>'
        else: raise ValueError(f'Unsupported Notion block: {kind}. Convert it to text or an image before publishing.')
    if list_kind: result += f'</{list_kind}>'
    return result

def export(api, root):
    # Stage a complete export before touching any previously published output.
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp); images = Images(stage); slugs=set(); stories=[]
        for page in api.pages():
            p = page['properties']
            if page.get('archived') or page.get('in_trash') or (p.get('Status',{}).get('select') or {}).get('name') != 'published': continue
            title = text(p['Title']); slug = text(p['Slug']).strip()
            if not slug: slug = re.sub('[^a-z0-9]+','-',title.lower()).strip('-') or page['id']
            if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug) or slug in slugs: raise ValueError('Slugs must be unique lowercase words separated by hyphens')
            slugs.add(slug)
            date = (p.get('Date',{}).get('date') or {}).get('start','')[:10]
            from datetime import date as Date
            Date.fromisoformat(date)
            if not title.strip(): raise ValueError('Published articles require a title')
            cover_files = p.get('Cover',{}).get('files',[])
            cover = images.save(cover_files[0] if cover_files else page.get('cover'))
            body = render(api.blocks(page['id']),images)
            meta = dict(layout='notion-article', title=title, summary=text(p.get('Summary',{})), date=date,
                category=(p.get('Category',{}).get('select') or {}).get('name','Field Notes'),location=text(p.get('Location',{})),
                cover=cover, published=True, notion=True, permalink=f'/adventures/journal/{slug}/')
            # Body is escaped HTML. Liquid raw prevents content from executing template tags.
            body = body.replace('{','&#123;').replace('}','&#125;')
            dest = stage/'_notion_articles'/('notion-'+page['id']+'.html'); dest.parent.mkdir(exist_ok=True)
            dest.write_text('---\n'+json.dumps(meta,ensure_ascii=False)+'\n---\n'+body)
            stories.append(dest.name)
        target = root/'_notion_articles'; target.mkdir(exist_ok=True)
        for old in target.glob('notion-*.html'): old.unlink()
        import shutil
        shutil.copytree(stage,root,dirs_exist_ok=True)
        print(f'Exported {len(stories)} published articles. Draft bodies were not requested.')

if __name__ == '__main__':
    try: export(API(),ROOT)
    except Exception as e:
        # Do not include response payloads, signed URLs, or credentials in CI logs.
        import sys
        print(str(e) if isinstance(e,(ValueError,RuntimeError)) else 'Publishing failed; check credentials, permissions and connectivity.',file=sys.stderr)
        sys.exit(1)
