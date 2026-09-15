"""
캠퍼스맵 아이소메트릭 투영.

지도를 바닥에 눕혀 놓고 비스듬히 내려다보는 모습으로 바꾼다.
평면을 ANGLE 만큼 돌린 뒤 세로로 SQUASH 만큼 눌러 주는 것이 전부다.

같은 변환을 배경 이미지(restyle_map.py)와 건물 좌표(build.py)에 함께 적용해야
건물이 지도 위 제자리에 선다. 그래서 계산을 이 파일 한 곳에 모아 둔다.
"""

import math

# 지도를 돌리는 각도(도). 음수면 시계 반대 방향.
ANGLE = -22.0
# 세로로 누르는 비율. 1 이면 위에서 그대로 내려다본 평면.
SQUASH = 0.62
# 건물이 솟아오르는 높이(투영 후 화면 픽셀).
HEIGHT = 74
# 건물이 잘리지 않도록 위쪽에 두는 여백.
PAD_TOP = HEIGHT + 16
PAD = 12

_C = math.cos(math.radians(ANGLE))
_S = math.sin(math.radians(ANGLE))


def _rotate(x, y):
    return x * _C - y * _S, (x * _S + y * _C) * SQUASH


def bounds(w, h):
    """원본 크기(w, h)를 투영했을 때의 좌표 범위와 결과 캔버스 크기."""
    pts = [_rotate(0, 0), _rotate(w, 0), _rotate(0, h), _rotate(w, h)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_u, min_v = min(xs), min(ys)
    out_w = math.ceil(max(xs) - min_u) + PAD * 2
    out_h = math.ceil(max(ys) - min_v) + PAD_TOP + PAD
    return min_u, min_v, out_w, out_h


def project(x, y, w, h):
    """원본 좌표 (x, y) 를 투영 후 화면 좌표로 옮긴다."""
    min_u, min_v, _, _ = bounds(w, h)
    u, v = _rotate(x, y)
    return u - min_u + PAD, v - min_v + PAD_TOP


def inverse_affine(w, h):
    """
    Pillow 의 Image.transform(AFFINE) 에 넘길 계수.

    Pillow 는 결과 좌표에서 원본 좌표를 거꾸로 찾아가므로 역변환이 필요하다.
        x = a*x' + b*y' + c
        y = d*x' + e*y' + f
    """
    min_u, min_v, _, _ = bounds(w, h)
    ox, oy = min_u - PAD, min_v - PAD_TOP
    a = _C
    b = _S / SQUASH
    d = -_S
    e = _C / SQUASH
    c = ox * a + oy * b
    f = ox * d + oy * e
    return (a, b, c, d, e, f)
