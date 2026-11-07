"""Check local links, leaked source files and root homepage integrity."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site').resolve()
assert (root/'index.html').read_bytes()==Path('index.html').read_bytes(), 'Root homepage changed'
for private in ('scripts','tests','_notion_articles','_stories','_data','requirements-notion.txt'):
    assert not (root/private).exists(), f'Source leaked: {private}'
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('href','src') or not value: continue
            p=urlsplit(value)
            if p.scheme or p.netloc or not p.path: continue
            path=(root/unquote(p.path).lstrip('/')) if p.path.startswith('/') else (current.parent/unquote(p.path))
            assert path.is_relative_to(root), 'Link escapes site'
            if path.is_dir(): path=path/'index.html'
            assert path.exists(), f'Broken local link in {current}: {value}'
for current in (root/'adventures').rglob('*.html'):
    body=current.read_text(); assert '{%' not in body and '{{' not in body, 'Unrendered template'
    Links().feed(body)
print('Root unchanged; local adventure links and source exclusion passed.')
