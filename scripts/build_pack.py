"""Validate a portable asset layout and generate SVG + Adobe JSX (stdlib only)."""
import argparse
import base64
import copy
import json
import math
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', XLINK)


def number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite number')
    if positive and value <= 0:
        raise ValueError('Expected a positive number')
    return value


def fields(obj, allowed):
    if not isinstance(obj, dict) or set(obj) - set(allowed.split()):
        raise ValueError('Unsupported fields: ' + repr(obj))


def asset_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Asset path must be relative')
    p = (root / relative).resolve()
    if not p.is_relative_to(root) or not p.is_file():
        raise ValueError('Missing or out-of-package asset: ' + relative)
    return p


def png_size(path):
    data = path.read_bytes()
    if len(data) < 33 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError('Not a PNG: ' + str(path))
    w, h = struct.unpack('>II', data[16:24])
    if not w or not h:
        raise ValueError('Empty PNG')
    return w, h


def vector(path, prefix):
    raw = path.read_text(encoding='utf-8-sig')
    if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
        raise ValueError('SVG entities are unsupported')
    tree = ET.fromstring(raw)
    if tree.tag != '{' + SVG + '}svg':
        raise ValueError('Expected SVG namespace')
    box = [float(v) for v in re.split(r'[\s,]+', tree.attrib.get('viewBox', '').strip())]
    if len(box) != 4 or box[:2] != [0, 0]:
        raise ValueError('SVG requires viewBox="0 0 width height"')
    number(box[2], True)
    number(box[3], True)
    allowed = {'svg', 'g', 'defs', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'linearGradient', 'radialGradient', 'stop', 'clipPath', 'title', 'desc', 'text', 'tspan', 'use'}
    ids = {}
    for e in tree.iter():
        if e.tag.split('}')[-1] not in allowed:
            raise ValueError('Unsupported SVG element: ' + e.tag)
        if 'id' in e.attrib:
            old = e.attrib['id']
            if old in ids:
                raise ValueError('Duplicate SVG id')
            ids[old] = prefix + '__' + old
        for k, v in e.attrib.items():
            key = k.split('}')[-1].lower()
            if key.startswith('on') or key in {'style', 'class', 'base'}:
                raise ValueError('Unsupported SVG attribute: ' + key)
            if key == 'href' and not v.startswith('#'):
                raise ValueError('External SVG reference')
            for ref in re.findall(r'url\((.*?)\)', v):
                if not ref.startswith('#') or not ref.endswith(tuple('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-:.')):
                    raise ValueError('Unsupported SVG URL')
    for e in tree.iter():
        for k, v in list(e.attrib.items()):
            if k == 'id':
                e.set(k, ids[v])
            elif k.split('}')[-1] == 'href':
                if v[1:] not in ids:
                    raise ValueError('Missing SVG reference')
                e.set(k, '#' + ids[v[1:]])
            elif 'url(' in v:
                def replace(m):
                    if m[1] not in ids:
                        raise ValueError('Missing SVG URL target')
                    return 'url(#' + ids[m[1]] + ')'
                e.set(k, re.sub(r'url\(#([^)]*)\)', replace, v))
    return tree, box[2:]


def ratio(actual, target, allow=False):
    if not allow and abs((actual[0] / actual[1]) / (target[0] / target[1]) - 1) > 0.001:
        raise ValueError('Aspect ratio mismatch; use correctly sized assets or explicit allow_distort')


PS_TEMPLATE = r'''#target photoshop
(function () {
  var pack = __DATA__;
  var base = File($.fileName).parent;
  var oldUnits = app.preferences.rulerUnits;
  var doc, src;
  function px(v) { return v.as('px'); }
  try {
    for (var j=0; j<pack.items.length; j++) {
      var a=pack.items[j];
      if(a.kind==='text') { app.fonts.getByName(a.ps_font); }
      else if(!File(base.fsName+'/'+(a.ps_file || a.file)).exists) { throw Error('Missing '+a.id); }
    }
    app.preferences.rulerUnits=Units.PIXELS;
    doc=app.documents.add(UnitValue(pack.canvas.width,'px'),UnitValue(pack.canvas.height,'px'),72,'Design asset pack',NewDocumentMode.RGB,DocumentFill.TRANSPARENT);
    for(var i=0;i<pack.items.length;i++) {
      var item=pack.items[i], layer;
      if(item.kind==='text') {
        layer=doc.artLayers.add(); layer.kind=LayerKind.TEXT;
        var t=layer.textItem;
        t.contents=item.text; t.font=item.ps_font;
        t.size=UnitValue(item.font_size,'pt');
        t.justification=Justification.LEFT;
        t.position=[UnitValue(item.x,'px'),UnitValue(item.y,'px')];
        var color=new SolidColor();color.rgb.hexValue=item.color.substring(1);t.color=color;
      } else {
        src=app.open(File(base.fsName+'/'+(item.ps_file || item.file)));
        layer=src.activeLayer.duplicate(doc,ElementPlacement.PLACEATBEGINNING);
        src.close(SaveOptions.DONOTSAVECHANGES);src=null;
        app.activeDocument=doc;doc.activeLayer=layer;
        executeAction(stringIDToTypeID('newPlacedLayer'),undefined,DialogModes.NO);
        layer=doc.activeLayer;
        var b=layer.bounds,w=px(b[2])-px(b[0]),h=px(b[3])-px(b[1]);
        if(w<=0 || h<=0) throw Error('Empty layer '+item.id);
        if(!item.allow_distort && Math.abs((w/h)/(item.width/item.height)-1)>0.001) throw Error('Visible bounds differ from file ratio: '+item.id+'. Trim transparent margins first.');
        layer.resize(100*item.width/w,100*item.height/h,AnchorPosition.TOPLEFT);
        b=layer.bounds;layer.translate(UnitValue(item.x-px(b[0]),'px'),UnitValue(item.y-px(b[1]),'px'));
        b=layer.bounds;
        if(Math.abs(px(b[0])-item.x)>1 || Math.abs(px(b[1])-item.y)>1 || Math.abs(px(b[2])-px(b[0])-item.width)>1 || Math.abs(px(b[3])-px(b[1])-item.height)>1) throw Error('Geometry verification failed: '+item.id);
      }
      layer.name=item.id;
    }
    alert('Imported into a NEW unsaved document. Check font, spacing and edges, then Save As PSD.');
  } catch(e) {
    alert('Import incomplete: '+e.message+'\nAny partial NEW document remains open for inspection. Existing documents were not saved.');
  } finally {
    if(src) { try { src.close(SaveOptions.DONOTSAVECHANGES); } catch(ignore) {} }
    app.preferences.rulerUnits=oldUnits;
  }
})();
'''


def build(root):
    root = Path(root).resolve()
    data = json.loads((root / 'layout.json').read_text(encoding='utf-8-sig'))
    fields(data, 'version canvas items')
    if data['version'] != 1:
        raise ValueError('Unsupported layout version')
    c = data['canvas']
    fields(c, 'width height')
    w, h = number(c['width'], True), number(c['height'], True)
    svg = ET.Element('{' + SVG + '}svg', {'width': str(w)+'px', 'height': str(h)+'px', 'viewBox': f'0 0 {w} {h}'})
    if not isinstance(data['items'], list) or not data['items']:
        raise ValueError('items must be non-empty')
    used = set()
    for item in data['items']:
        kind = item['kind']
        fields(item, 'id kind x y text font_size font_family ps_font color' if kind == 'text' else 'id kind x y width height file ps_file allow_distort')
        name = item['id']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', name) or '__' in name or name in used:
            raise ValueError('Invalid or duplicate item id')
        used.add(name)
        x, y = number(item['x']), number(item['y'])
        group = ET.SubElement(svg, '{'+SVG+'}g', {'id': name})
        if kind == 'text':
            if not isinstance(item['text'], str) or not item['text'] or '\n' in item['text'] or '\r' in item['text']:
                raise ValueError('Only non-empty single-line text supported')
            if not all(isinstance(item.get(k), str) and item[k] for k in ('font_family', 'ps_font')):
                raise ValueError('Both font family and PostScript name required')
            if not re.fullmatch(r'#[0-9a-fA-F]{6}', item['color']):
                raise ValueError('Expected hex color')
            ET.SubElement(group, '{'+SVG+'}text', {'x': str(x), 'y': str(y), 'font-size': str(number(item['font_size'], True)), 'font-family': item['font_family'], 'fill': item['color'], '{http://www.w3.org/XML/1998/namespace}space': 'preserve'}).text = item['text']
            continue
        iw, ih = number(item['width'], True), number(item['height'], True)
        allow = item.get('allow_distort', False)
        if not isinstance(allow, bool):
            raise ValueError('allow_distort must be boolean')
        p = asset_path(root, item['file'])
        if kind == 'raster':
            ratio(png_size(p), (iw, ih), allow)
            if 'ps_file' in item:
                raise ValueError('ps_file is only for vectors')
            image = ET.SubElement(group, '{'+SVG+'}image', {'x': str(x), 'y': str(y), 'width': str(iw), 'height': str(ih), 'preserveAspectRatio': 'none'})
            image.set('{'+XLINK+'}href', 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii'))
        elif kind == 'vector':
            node, size = vector(p, name)
            ratio(size, (iw, ih), allow)
            ratio(png_size(asset_path(root, item['ps_file'])), size)
            node = copy.deepcopy(node)
            node.set('x', str(x)); node.set('y', str(y))
            node.set('width', str(iw)); node.set('height', str(ih))
            node.set('preserveAspectRatio', 'none')
            group.append(node)
        else:
            raise ValueError('Unsupported item kind')
    ps_json = json.dumps(data, ensure_ascii=True).replace('</', '<\\/')
    outputs = {
        'composition.svg': ET.tostring(svg, encoding='unicode'),
        'import-photoshop.jsx': PS_TEMPLATE.replace('__DATA__', ps_json),
        'open-illustrator.jsx': '#target illustrator\n(function(){var f=File(File($.fileName).parent.fsName+"/composition.svg");if(!f.exists)throw Error("Missing composition.svg");app.open(f);alert("Opened composition SVG. Inspect groups, paths, fonts and images, then Save As AI. No existing document was saved.");})();\n',
        '使用说明.txt': '先看 preview.png（由制作者另行渲染）。\nPhotoshop：文件 > 脚本 > 浏览，运行 import-photoshop.jsx。\nIllustrator：直接打开 composition.svg，或运行 open-illustrator.jsx。\nPNG 是独立位图；SVG 图案是矢量；文字需要安装指定字体。PS 图案为智能对象，文字独立。\n脚本不自动保存，请核对后另存 PSD/AI。所有素材需随包保留。\n自动构建检查不等于 Adobe 实机验证。几何读回允许 1 px 光栅误差，更严格需求应人工或专用逻辑核验。\n',
    }
    for name in outputs:
        if (root / name).exists():
            raise FileExistsError('Refusing overwrite: ' + str(root / name))
    for name, content in outputs.items():
        (root / name).write_text(content, encoding='utf-8-sig' if name.endswith('.jsx') else 'utf-8')
    return list(outputs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', type=Path)
    args = parser.parse_args()
    try:
        print('\n'.join(build(args.pack)))
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError) as exc:
        parser.exit(1, 'Build failed: ' + str(exc) + '\n')
