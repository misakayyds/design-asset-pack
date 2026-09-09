import copy
import importlib.util
import json
from pathlib import Path
import uuid
import unittest
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build_pack.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class PackTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT/'work'/('test-'+uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        (self.root/'assets').mkdir()
        Image.new('RGBA', (100, 100), '#FFAA33').save(self.root/'assets/square.png')
        (self.root/'assets/square.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><linearGradient id="g"><stop offset="0" stop-color="#ffaa33"/><stop offset="1" stop-color="#ee3366"/></linearGradient></defs><rect width="100" height="100" fill="url(#g)"/></svg>')
        self.data = {'version':1,'canvas':{'width':640,'height':360},'items':[
            {'id':'square','kind':'vector','file':'assets/square.svg','ps_file':'assets/square.png','x':12.5,'y':24,'width':80,'height':80},
            {'id':'label','kind':'text','text':'素材 < & test','x':120,'y':70,'font_size':28,'font_family':'Arial','ps_font':'ArialMT','color':'#333333'}]}

    def run_pack(self):
        (self.root/'layout.json').write_text(json.dumps(self.data),encoding='utf-8')
        return b.build(self.root)

    def tearDown(self):
        pass  # Preserve scoped test evidence; no deletion.

    def test_build_preserves_geometry_text_and_references(self):
        self.run_pack()
        root=ET.parse(self.root/'composition.svg').getroot()
        ns={'s':b.SVG}
        inner=root.find('s:g/s:svg',ns)
        self.assertEqual(inner.get('x'),'12.5')
        self.assertEqual(inner.find('s:rect',ns).get('fill'),'url(#square__g)')
        self.assertEqual(root.find('.//s:text',ns).text,'素材 < & test')
        before=(self.root/'composition.svg').read_bytes()
        with self.assertRaises(FileExistsError):self.run_pack()
        self.assertEqual(before,(self.root/'composition.svg').read_bytes())

    def test_rejects_distortion(self):
        self.data['items'][0]['width']=90
        with self.assertRaises(ValueError):self.run_pack()
        self.assertFalse((self.root/'composition.svg').exists())

    def test_explicit_distortion(self):
        self.data['items'][0].update(width=90,allow_distort=True)
        self.run_pack()

    def test_rejects_unknown_transform(self):
        self.data['items'][0]['rotation']=30
        with self.assertRaises(ValueError):self.run_pack()

    def test_rejects_outside_path(self):
        self.data['items'][0]['file']='../outside.svg'
        with self.assertRaises(ValueError):self.run_pack()

    def test_rejects_active_svg(self):
        (self.root/'assets/square.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><script>alert(1)</script></svg>')
        with self.assertRaises(ValueError):self.run_pack()

    def test_rejects_nan(self):
        self.data['items'][0]['x']=float('nan')
        with self.assertRaises(ValueError):self.run_pack()

    def test_rejects_duplicate_ids(self):
        self.data['items'].append(copy.deepcopy(self.data['items'][0]))
        with self.assertRaises(ValueError):self.run_pack()


if __name__=='__main__':unittest.main()
