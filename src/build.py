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
         styles=(), scripts=(), sidemenu=(), **ctx):
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
        styles=asset("css", styles),
        scripts=asset("js", scripts),
        content=env.render(template, common),
    )))


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
        body_class="page-home", styles=["index.css", "nav.css"],
        scripts=["carousel.js", "popup.js"], **home))

    made.append(page(
        "campusMap.html", "campusmap.html",
        title=f"캠퍼스맵 · {SITE['title']}",
        description="한동대학교 캠퍼스 지도에서 건물을 골라 자세히 살펴보세요.",
        body_class="page-map", styles=["campusMap.css", "nav.css"],
        scripts=["typing.js", "responsive.js"], **cmap))

    made.append(page(
        "introduce.html", "introduce.html",
        title=f"소개 · {SITE['title']}",
        description="한캠사를 만든 이유와 만든 사람들, 그리고 앱 프로그래밍 과목을 소개합니다.",
        body_class="page-introduce",
        styles=["introduce.css", "nav.css", "sideMenubar.css"],
        scripts=["typing.js"],
        sidemenu=[{"href": "#section_1", "label": "사이트 소개"},
                  {"href": "#section_2", "label": "개발자 소개"},
                  {"href": "#section_3", "label": "과목 소개"}],
        **intro))

    made.append(page(
        "popup.html", "popup.html",
        title=f"환영합니다 · {SITE['title']}",
        description="한캠사 소개 안내",
        body_class="page-popup", styles=["popup.css"], scripts=["popup.js"]))

    made.append(page(
        "404.html", "notfound.html",
        title=f"페이지를 찾을 수 없습니다 · {SITE['title']}",
        description="요청하신 페이지가 없습니다.",
        body_class="page-404", styles=["notfound.css"]))

    made.append(page(
        "first.html", "first.html",
        title=SITE["title"], description="한캠사",
        body_class="page-first", styles=["first.css"],
        scripts=["https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"]))

    # 3. 건물 페이지
    for b in buildings:
        made.append(page(
            f"html/{b['code']}.html", "building.html",
            title=f"{b['name']} · {SITE['title']}",
            description=b["desc"].lstrip(": ")[:150],
            body_class="page-building",
            styles=["Building.css", "nav.css", "sideMenubar.css"],
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
            styles=["Building.css", "nav.css", "HotPlace.css"],
            h=h))

    print(f"{len(made)}개 페이지 생성 -> build/")
    return made


if __name__ == "__main__":
    build()
