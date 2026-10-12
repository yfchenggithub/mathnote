#!/usr/bin/env python3
"""Compose a fixed-position original-WeChat-QR brand overlay over a blank-reserved rose card.
Usage: python apply_brand.py VISUAL_CARD.png FINAL_CARD.png
"""
from pathlib import Path
from PIL import Image
import cv2
import json
import sys

base_dir=Path(__file__).resolve().parent
expected=json.loads((base_dir/'brand_config.json').read_text(encoding='utf-8'))['wechat_qr_payload']
if len(sys.argv)!=3:
    raise SystemExit('用法：python apply_brand.py <无二维码底图.png> <成品.png>')
in_path=Path(sys.argv[1]); out_path=Path(sys.argv[2])
base=Image.open(in_path).convert('RGBA')
W,H=base.size
brand_path=base_dir/f'brand_overlay_{W}x{H}.png'
if not brand_path.exists():
    raise SystemExit(f'不支持 {W}x{H} 画布；仅支持 941x1672、1080x1920。禁止嵌入后整图缩放。')
overlay=Image.open(brand_path).convert('RGBA')
# Draw a consistent origin-exact brand overlay; reserve clean white in the bottom right first.
final=Image.alpha_composite(base,overlay).convert('RGB')
out_path.parent.mkdir(exist_ok=True,parents=True)
final.save(out_path,format='PNG')
val, pts, _=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(out_path)))
print('输出：',out_path)
print('二维码解码：', 'PASS' if val==expected else 'FAIL / NOT VERIFIED')
if val!=expected:
    raise SystemExit('二维码未通过整图自动解码，请检查预留空白和最终内容，切勿直接放大二维码。')
print('微信真机验收：PENDING（需要你用微信扫描成品确认）')
