"""Create original geometric test assets; no image service or credentials needed."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw


def create(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    assets = root/'assets'
    assets.mkdir()
    Image.new('RGB', (640,360), '#182534').save(assets/'background.png')
    (assets/'diamond.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M50 0 L100 50 L50 100 L0 50 Z" fill="#F2B84B"/></svg>',encoding='utf-8')
    diamond=Image.new('RGBA',(100,100),(0,0,0,0))
    ImageDraw.Draw(diamond).polygon([(50,0),(99,50),(50,99),(0,50)],fill='#F2B84B')
    diamond.save(assets/'diamond.png')
    layout={'version':1,'canvas':{'width':640,'height':360},'items':[
        {'id':'background','kind':'raster','file':'assets/background.png','x':0,'y':0,'width':640,'height':360},
        {'id':'diamond','kind':'vector','file':'assets/diamond.svg','ps_file':'assets/diamond.png','x':64,'y':100,'width':100,'height':100},
        {'id':'title','kind':'text','text':'DESIGN ASSET PACK','x':196,'y':156,'font_size':24,'font_family':'Arial','ps_font':'ArialMT','color':'#FFFFFF'}]}
    (root/'layout.json').write_text(json.dumps(layout,indent=2),encoding='utf-8')
    print(root)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    create(parser.parse_args().output)
