"""Create diagnostic mattes and alpha statistics; never modify source assets."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw


def audit(source, output):
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    report = {}
    for path in sorted(source.glob('*.png')):
        with Image.open(path) as im:
            rgba = im.convert('RGBA')
        alpha = rgba.getchannel('A')
        hist = alpha.histogram()
        report[path.name] = {
            'size': list(rgba.size),
            'transparent_pixels': hist[0], 'opaque_pixels': hist[255],
            'partial_pixels': sum(hist[1:255]),
            'faint_pixels_alpha_1_31': sum(hist[1:32]),
            'bounds_alpha_gt_0': alpha.getbbox(),
            'bounds_alpha_ge_128': alpha.point(lambda x: 255 if x >= 128 else 0).getbbox(),
            'review_status': 'needs_visual_review',
        }
        # Diagnostics only: source RGB and alpha are untouched on disk.
        thumb = rgba.copy()
        thumb.thumbnail((600, 420), Image.Resampling.LANCZOS)
        cell_w, cell_h = 640, 460
        sheet = Image.new('RGB', (cell_w*2, cell_h*2), '#cccccc')
        draw = ImageDraw.Draw(sheet)
        for idx, (label, color) in enumerate([('WHITE', '#ffffff'), ('BLACK', '#000000'), ('MAGENTA', '#ff00ff'), ('ALPHA', '#000000')]):
            xx, yy = (idx % 2)*cell_w, (idx // 2)*cell_h
            tile = Image.new('RGBA', thumb.size, color)
            tile = Image.alpha_composite(tile, thumb).convert('RGB') if idx < 3 else thumb.getchannel('A').convert('RGB')
            sheet.paste(tile, (xx+20, yy+30))
            draw.text((xx+20, yy+8), label, fill='black')
        sheet.save(output/(path.stem+'-matte-review.png'))
        # Full-resolution enlarged view catches tiny specks that overview hides.
        if rgba.width <= 600 and rgba.height <= 420:
            for label, color in [('white', 'white'), ('magenta', '#ff00ff')]:
                matte=Image.alpha_composite(Image.new('RGBA', rgba.size,color),rgba)
                matte.resize((rgba.width*4,rgba.height*4),Image.Resampling.NEAREST).save(output/(path.stem+'-'+label+'-4x.png'))
    (output/'alpha-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2),encoding='utf-8')
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(audit(args.assets,args.output),ensure_ascii=False,indent=2))
