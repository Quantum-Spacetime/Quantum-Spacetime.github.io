import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('publish', 'scripts/notion/publish.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def prop(value,kind='rich_text'): return {'type':kind,kind:[{'plain_text':value}]}
def page(status='published',slug='alpine-walk',id='abc'):
 return {'id':id,'properties':{'Title':prop('Alpine <walk>','title'),'Slug':prop(slug),'Status':{'select':{'name':status}},'Date':{'date':{'start':'2026-11-07'}}}}
class Fake:
 def __init__(self,pages): self.entries=pages;self.requested=[]
 def pages(self): return iter(self.entries)
 def blocks(self,id): self.requested.append(id);return [{'type':'paragraph','paragraph':{'rich_text':[{'plain_text':'Hello {{ site.secret }} <script>bad</script>'}]}}]
class Tests(unittest.TestCase):
 def test_drafts_and_removal(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); (r/'_notion_articles').mkdir();(r/'_notion_articles/notion-old.html').write_text('old');(r/'_notion_articles/legacy.md').write_text('legacy')
   api=Fake([page(),page('draft','private','private')]);m.export(api,r)
   self.assertEqual(api.requested,['abc']); self.assertFalse((r/'_notion_articles/notion-old.html').exists());self.assertTrue((r/'_notion_articles/legacy.md').exists())
   s=(r/'_notion_articles/notion-abc.html').read_text();self.assertNotIn('<script>',s);self.assertNotIn('{{',s);self.assertNotIn('private',s)
   m.export(Fake([]),r); self.assertFalse((r/'_notion_articles/notion-abc.html').exists())
 def test_failure_preserves_previous(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'_notion_articles').mkdir();p=r/'_notion_articles/notion-old.html';p.write_text('old')
   for pages in ([page(slug='../escape')],[page(),page(id='other')]):
    with self.assertRaises(ValueError):m.export(Fake(pages),r)
    self.assertEqual(p.read_text(),'old')
 def test_url_and_block_safety(self):
  self.assertEqual(m.safe_url('javascript:alert(1)'),'#')
  with self.assertRaises(ValueError):m.render([{'type':'unsupported'}],None)
  with self.assertRaises(ValueError):m.check_host('https://127.0.0.1/a.png')
  with self.assertRaises(ValueError):m.check_host('http://example.com/a.png')
 def test_image_optimization(self):
  import io
  image=io.BytesIO();m.Image.new('RGB',(3000,1000),'green').save(image,'JPEG',exif=b'Exif\x00\x00')
  class Response(io.BytesIO): pass
  class Opener:
   def open(self,*a,**kw):return Response(image.getvalue())
  with tempfile.TemporaryDirectory() as d,patch.object(m,'check_host'),patch.object(m.urllib.request,'build_opener',return_value=Opener()):
   path=m.Images(Path(d)).save({'type':'file','file':{'url':'https://example.com/image?signature=secret'}})
   data=(Path(d)/path.lstrip('/')).read_bytes();self.assertNotIn(b'Exif',data)
   with m.Image.open(io.BytesIO(data)) as im:self.assertLessEqual(im.width,2400);self.assertEqual(im.format,'WEBP')
   self.assertNotIn('signature',path)
if __name__=='__main__':unittest.main()
