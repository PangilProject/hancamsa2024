#!/usr/bin/env python3
"""
캠퍼스 지도 배경을 디자인 팔레트로 다시 칠한다.

원본은 지도 서비스 스크린샷처럼 보이는 평면 지도다.
색 종류가 몇 개 안 되므로, 픽셀을 의미별로 분류해 브랜드 색으로 바꾸고
뭉개진 경계를 정리하면 직접 그린 일러스트에 가까운 결과가 나온다.

    python3 src/tools/restyle_map.py
"""

import os
import sys

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import mapproj  # noqa: E402

SRC = "src/assets/image/_source/mainMap-original.webp"
DST = "src/assets/image/mainMap.webp"

# 디자인 시스템과 맞춘 목표 색
ROAD = (255, 255, 255)        # 길
BUILDING = (233, 238, 246)    # 핫스팟이 아닌 건물
GROUND = (203, 214, 230)      # 캠퍼스 지면
GROUND_DIM = (188, 200, 219)  # 지면 그늘
OUTSIDE = (240, 235, 225)     # 캠퍼스 밖
GRASS = (185, 223, 196)       # 잔디·운동장
COURT = (238, 201, 164)       # 코트


def classify(rgb):
    """픽셀 색 하나를 지도 요소로 분류한다. 순서가 중요하다."""
    r, g, b = rgb
    light = (r + g + b) / 3
    if g > r + 6 and g > b + 6:
        return GRASS
    if r > b + 18 and r >= g:
        return COURT
    if r > b + 6 and light > 220:
        return OUTSIDE
    if light >= 250:
        return ROAD
    if light >= 232:
        return BUILDING
    if b > r and light > 196:
        return GROUND
    return GROUND_DIM


def main():
    im = Image.open(SRC).convert("RGB")

    # 색 수를 줄여 분류를 안정시킨다
    reduced = im.quantize(colors=24, method=Image.MEDIANCUT)
    palette = reduced.getpalette()[: 24 * 3]
    mapped = []
    for i in range(24):
        mapped.extend(classify(tuple(palette[i * 3:i * 3 + 3])))
    reduced.putpalette(mapped + [0] * (768 - len(mapped)))

    out = reduced.convert("RGB")
    # 경계에 남은 잡티를 정리해 면을 평평하게 만든다
    out = out.filter(ImageFilter.ModeFilter(size=3))

    # 바닥에 눕혀 비스듬히 내려다보는 모습으로 투영한다
    w, h = out.size
    _, _, out_w, out_h = mapproj.bounds(w, h)
    out = out.convert("RGBA").transform(
        (out_w, out_h), Image.AFFINE, mapproj.inverse_affine(w, h),
        resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    out.save(DST, "WEBP", quality=94, method=6)

    print(f"{DST}  {out.size[0]}x{out.size[1]}  {os.path.getsize(DST)/1024:.0f} KB")


if __name__ == "__main__":
    main()
