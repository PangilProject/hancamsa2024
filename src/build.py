#!/usr/bin/env python3
"""
한캠사 정적 사이트 빌드 스크립트.

    python3 src/build.py

src/templates + src/data + src/assets 를 읽어 build/ 를 통째로 다시 만든다.
build/ 안의 내용은 전부 생성물이므로 직접 고치지 말 것. 수정은 src/ 에서 한다.
"""

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapproj  # noqa: E402
from render import Env  # noqa: E402

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT = os.path.join(ROOT, "build")

env = Env(os.path.join(SRC, "templates"))


def data(name):
    with open(os.path.join(SRC, "data", name), encoding="utf-8") as f:
        return json.load(f)


SITE = data("site.json")


def write(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def page(path, template, *, title, description, body_class,
         styles=(), scripts=(), sidemenu=(), chrome=True, **ctx):
    """템플릿 하나를 공통 레이아웃에 끼워 넣어 한 페이지를 만든다."""
    base = "../" * path.count("/")
    common = dict(ctx, site=SITE, base=base, sidemenu=list(sidemenu))
    # 외부 URL 은 그대로, 나머지는 페이지 깊이에 맞춰 경로를 붙인다
    def asset(kind, items):
        return [i if i.startswith("http") else f"{base}{kind}/{i}" for i in items]
    return write(path, env.render("_layout.html", dict(
        common,
        title=title,
        description=description,
        body_class=body_class,
        chrome=chrome,
        styles=asset("css", styles),
        scripts=asset("js", scripts),
        content=env.render(template, common),
    )))


def map_view(cmap):
    """투영 후 캔버스 크기. SVG viewBox 와 배경 이미지 크기가 여기에 맞춰진다."""
    _, _, w, h = mapproj.bounds(cmap["image"]["w"], cmap["image"]["h"])
    return {"w": w, "h": h}


def map_shapes(cmap):
    """
    캠퍼스맵 건물을 아이소메트릭 입체 블록으로 만든다.

    1. usemap 시절 좌표(1036.8 x 520 기준)를 원본 이미지 비율로 옮기고
    2. 배경 이미지와 똑같은 방식으로 투영한 뒤
    3. 바닥면을 HEIGHT 만큼 위로 올린 윗면과, 두 면을 잇는 옆면을 만든다.
    """
    gw, gh = cmap["image"]["w"], cmap["image"]["h"]
    sx = gw / cmap["coord_space"]["w"]
    sy = gh / cmap["coord_space"]["h"]
    h = mapproj.HEIGHT

    def fmt(pts):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    out = []
    for a in cmap["areas"]:
        n = [float(v) for v in a["coords"].replace(",", " ").split()]
        if a["shape"] == "rect":
            x1, y1, x2, y2 = n
            raw = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        else:
            raw = list(zip(n[0::2], n[1::2]))

        ground = [mapproj.project(x * sx, y * sy, gw, gh) for x, y in raw]
        top = [(x, y - h) for x, y in ground]

        # 바닥면과 윗면을 잇는 옆면. 뒤쪽 면은 윗면에 가려지므로 전부 그려도 된다.
        walls = []
        for i in range(len(ground)):
            j = (i + 1) % len(ground)
            walls.append(fmt([ground[i], ground[j], top[j], top[i]]))

        xs = [p[0] for p in top]
        ys = [p[1] for p in top]
        out.append(dict(
            a,
            top=fmt(top),
            walls=walls,
            cx=round((min(xs) + max(xs)) / 2 + a.get("label_dx", 0), 1),
            cy=round((min(ys) + max(ys)) / 2 + a.get("label_dy", 0), 1),
            # 화면 아래쪽에 있을수록 보는 사람과 가깝다
            depth=sum(p[1] for p in ground) / len(ground),
        ))

    # 뒤쪽 건물부터 그려야 앞 건물이 제대로 가린다
    out.sort(key=lambda s: s["depth"])
    return out


def chunk(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def build():
    # 1. build/ 를 비우고 정적 에셋을 복사한다
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for name in ("css", "js", "image"):
        shutil.copytree(os.path.join(SRC, "assets", name), os.path.join(OUT, name))

    made = []
    buildings = data("buildings.json")
    hotplaces = data("hotplaces.json")
    home = data("home.json")
    cmap = data("campusmap.json")
    intro = data("introduce.json")

    alts = ["한동대학교 캠퍼스 전경", "한동대학교 캠퍼스 풍경", "한동대학교 캠퍼스 잔디밭"]
    for i, s in enumerate(home["slides"]):
        s["alt"] = alts[i] if i < len(alts) else "한동대학교 캠퍼스"

    # 2. 단독 페이지
    made.append(page(
        "index.html", "home.html",
        title=f"{SITE['title']} · {SITE['tagline']}",
        description="한동대학교의 건물과 캠퍼스 곳곳을 소개하는 사이트입니다.",
        body_class="page-home", styles=["home.css"],
        scripts=["nav.js", "carousel.js", "popup.js"], **home))

    made.append(page(
        "campusMap.html", "campusmap.html",
        title=f"캠퍼스맵 · {SITE['title']}",
        description="한동대학교 캠퍼스 지도에서 건물을 골라 자세히 살펴보세요.",
        body_class="page-map", styles=["campusmap.css"],
        shapes=map_shapes(cmap), view=map_view(cmap), **cmap))

    made.append(page(
        "introduce.html", "introduce.html",
        title=f"소개 · {SITE['title']}",
        description="한캠사를 만든 이유와 만든 사람들, 그리고 앱 프로그래밍 과목을 소개합니다.",
        body_class="page-introduce",
        styles=["introduce.css"],
        sidemenu=[{"href": "#section_1", "label": "사이트 소개"},
                  {"href": "#section_2", "label": "개발자 소개"},
                  {"href": "#section_3", "label": "과목 소개"}],
        **intro))

    made.append(page(
        "popup.html", "popup.html",
        title=f"환영합니다 · {SITE['title']}",
        description="한캠사 소개 안내",
        body_class="page-popup", styles=["popup.css"], scripts=["popup.js"], chrome=False))

    made.append(page(
        "404.html", "notfound.html",
        title=f"페이지를 찾을 수 없습니다 · {SITE['title']}",
        description="요청하신 페이지가 없습니다.",
        body_class="page-404", styles=["notfound.css"], chrome=False))

    made.append(page(
        "first.html", "first.html",
        title=SITE["title"], description="한캠사",
        body_class="page-first", styles=["first.css"], chrome=False,
        scripts=["https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"]))

    # 3. 건물 페이지
    for b in buildings:
        made.append(page(
            f"html/{b['code']}.html", "building.html",
            title=f"{b['name']} · {SITE['title']}",
            description=b["desc"].lstrip(": ")[:150],
            body_class="page-building",
            styles=["building.css"], scripts=["nav.js"],
            sidemenu=[{"href": "#section_3", "label": "건물 소개"},
                      {"href": "#section_2", "label": "핫플레이스"}],
            b=b, rows=chunk(b["hotplaces"], 4)))

    # 4. 핫플레이스 상세
    for h in hotplaces:
        made.append(page(
            f"html/info/{h['slug']}.html", "hotplace.html",
            title=f"{h['title']} · {SITE['title']}",
            description=(h["body"][0] if h["body"] else h["title"])[:150],
            body_class="page-info",
            styles=["hotplace.css"],
            h=h))

    print(f"{len(made)}개 페이지 생성 -> build/")
    return made


if __name__ == "__main__":
    build()
