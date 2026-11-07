"""Exercise content changes against real Jekyll builds in an isolated temporary copy."""
import argparse
import base64
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--jekyll', default='bundle exec jekyll')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='quiet-atlas-check-') as tmp:
    source = Path(tmp) / 'source'
    shutil.copytree(root, source, ignore=shutil.ignore_patterns('.git', '_site', 'vendor', '.bundle'))
    target = Path(tmp) / 'site'
    def build():
        subprocess.run(shlex.split(args.jekyll) + ['build', '--strict_front_matter', '--source', str(source), '--destination', str(target)], cwd=source, check=True, stdout=subprocess.DEVNULL)
        page = (target / 'adventures/index.html').read_text()
        assert '{{' not in page and '{%' not in page, 'Unrendered Liquid'
        assert (target / 'index.html').read_bytes() == (root / 'index.html').read_bytes(), 'Root homepage changed'
        assert not (target / '_stories').exists(), 'Story sources leaked into build'
        assert not (target / '_data').exists(), 'Settings source leaked into build'
        return page
    page = build()
    assert page.count('<article class="story">') == 3
    assert page.count('<figure class="gallery-item">') == 3
    assert 'This is a demonstration of how a longer travel entry' in page
    assert 'https://app.pagescms.org/' in (target / 'adventures/admin/index.html').read_text()
    story = source / '_stories/verification.md'
    data = dict(title='Verification <title>', published=True, date='2026-11-07', category='TEST / ALPS', sample=False, cover='/adventures/images/verify.png', alt='A "test" photograph', summary='Create a story')
    def write(body):
        story.write_text('---\n' + json.dumps(data) + '\n---\n' + body)
    image = source / 'adventures/images/verify.png'
    image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
    write('<p>Created body</p>')
    page = build()
    assert page.count('<article class="story">') == 4
    assert 'Verification &lt;title&gt;' in page and '<p>Created body</p>' in page
    assert 'alt="A &quot;test&quot; photograph"' in page
    assert page.index('Verification &lt;title&gt;') < page.index('Between the peaks')
    assert (target / 'adventures/images/verify.png').read_bytes() == image.read_bytes()
    data['cover'] = '/adventures/images/replacement.png'
    image.rename(source / 'adventures/images/replacement.png')
    write('<p>Edited body</p><img src="/adventures/images/replacement.png" alt="Inline photo">')
    settings = json.loads((source / '_data/adventures.json').read_text())
    settings['hero_image'] = data['cover']
    settings['gallery'][0]['image'] = data['cover']
    settings['gallery'][0]['caption'] = 'Changed gallery caption'
    (source / '_data/adventures.json').write_text(json.dumps(settings))
    page = build()
    assert '<p>Edited body</p>' in page and 'Created body' not in page
    assert page.count('/adventures/images/replacement.png') == 4
    assert 'Changed gallery caption' in page
    data['published'] = False
    write('<p>Hidden draft body</p>')
    page = build()
    assert page.count('<article class="story">') == 3
    assert 'Hidden draft body' not in page and 'Verification &lt;title&gt;' not in page
    story.unlink()
    assert build().count('<article class="story">') == 3
    for item in (source / '_stories').glob('*.md'):
        item.unlink()
    page = build()
    assert '<article class="story">' not in page and 'New stories are on their way.' in page
print('PASS: migration, homepage bytes, create, edit, ordering, escaping, image replacement, gallery, hide, delete, empty journal, editor link')
