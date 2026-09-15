# hancamsa

안녕하세요 한동대학교 캠퍼스 소개를 도와주는 '한캠사' 웹사이트 입니다.

한동대학교 캠퍼스를 소개하는 다양한 페이지로 구성되어 있습니다.

## 구성인원

- 20학번 김광일
- 20학번 고준석
- 20학번 고나연
- 19학번 허정현

## 폴더 구조

`build/` 는 **전부 생성물**입니다. 직접 고치지 말고 `src/` 를 고친 뒤 빌드하세요.

```
src/
├── build.py          빌드 스크립트 (여기를 실행)
├── render.py         작은 템플릿 엔진 (외부 의존성 없음)
├── mapproj.py        캠퍼스맵 아이소메트릭 투영 계산
├── templates/        HTML 템플릿 - _ 로 시작하면 공통 조각
├── data/             페이지 내용 (JSON)
├── tools/            가끔 돌리는 도구 (지도 이미지 생성 등)
└── assets/           css / js / image 원본
        ↓  python3 src/build.py
build/                배포되는 정적 사이트 (64개 페이지)
```

## 빌드

```bash
python3 src/build.py
```

파이썬 3.8 이상만 있으면 됩니다. 별도 패키지 설치는 필요 없습니다.
실행하면 `build/` 를 통째로 지우고 다시 만듭니다.

## 어디를 고쳐야 하나요

| 하고 싶은 일 | 고칠 곳 |
| --- | --- |
| 메뉴·사이트 이름 변경 | `src/data/site.json` |
| 건물 설명, 핫플레이스 목록 변경 | `src/data/buildings.json` |
| 핫플레이스 상세 내용 변경 | `src/data/hotplaces.json` |
| 소개 페이지 내용 변경 | `src/data/introduce.json` |
| 캠퍼스맵 클릭 영역 변경 | `src/data/campusmap.json` |
| 모든 페이지의 헤더 변경 | `src/templates/_nav.html` (한 곳만 고치면 전부 반영) |
| 레이아웃·디자인 변경 | `src/assets/css/` |
| 색·라운드·여백 기준값 변경 | `src/assets/css/base.css` 맨 위 `:root` |
| 캠퍼스맵 건물 이름표 위치 | `src/data/campusmap.json` 의 `label_dx` / `label_dy` |

## 페이지 구성

- `index.html` — 메인 (히어로 캐러셀)
- `campusMap.html` — 캠퍼스 지도. 건물을 클릭하면 상세로 이동
- `introduce.html` — 사이트·개발자·과목 소개
- `html/*.html` — 건물 11곳
- `html/info/*.html` — 핫플레이스 47곳

## 디자인 시스템

색·라운드·여백·그림자는 `src/assets/css/base.css` 의 `:root` 에 토큰으로 모여 있습니다.
값을 바꾸면 사이트 전체에 반영됩니다.

- 색은 회색 계열 + 포인트 블루(`--blue`) 하나로 제한합니다
- 라운드는 8 / 12 / 16 / 20 네 단계만 씁니다
- 경계선 대신 배경색 차이와 옅은 그림자로 면을 나눕니다
- 본문 글꼴은 Pretendard 를 CDN 에서 불러옵니다

공통 UI 조각: `.card` `.btn` `.chip` `.tabs` `.nav` `.footer` `.page-head` `.section-title`


## 캠퍼스맵

지도는 배경 이미지 위에 건물을 SVG 입체 블록으로 세워 그립니다.

1. `src/tools/restyle_map.py` 가 원본 지도를 브랜드 색으로 다시 칠하고
   아이소메트릭으로 투영해 `src/assets/image/mainMap.webp` 를 만듭니다.
   원본은 `src/assets/image/_source/` 에 보관되어 있습니다.
2. `src/build.py` 가 `src/data/campusmap.json` 의 건물 좌표에 **같은 투영**을 적용해
   윗면과 옆면 폴리곤을 만듭니다. 계산은 `src/mapproj.py` 한 곳에 있습니다.

지도 각도나 건물 높이를 바꾸려면 `src/mapproj.py` 의 `ANGLE` / `SQUASH` / `HEIGHT` 를 고친 뒤

```bash
python3 src/tools/restyle_map.py   # 배경 다시 만들기
python3 src/build.py               # 건물 좌표 다시 계산
```

두 개를 **반드시 함께** 돌려야 건물이 지도 위 제자리에 섭니다.

좁은 화면에서는 건물 블록이 누르기에 너무 작아, 지도는 전경만 보여주고
이동은 아래 칩 목록으로 하게 되어 있습니다.


## 반응형

브레이크포인트는 `src/assets/css/responsive.css` 한 곳에 모여 있습니다.

- ~1024px 태블릿 가로
- ~768px 태블릿 세로·큰 폰 — 2단 배치가 세로로 쌓이고, 카드 그리드가 2열이 됩니다
- ~480px 폰

## 이미지

`src/assets/image/` 에 넣습니다. 원본 사진을 그대로 넣지 말고 **긴 변 1600px, WebP** 로 변환해서 넣어주세요.

```bash
# 예시 (Pillow 필요)
python3 -c "
from PIL import Image
im = Image.open('원본.jpg'); w, h = im.size
r = 1600 / max(w, h)
if r < 1: im = im.resize((round(w*r), round(h*r)), Image.LANCZOS)
im.save('결과.webp', 'WEBP', quality=82, method=6)"
```

## 알려진 사항

- `html/info/communication-office.html` (커뮤니케이션학부 사무실) 은 내용이 아직 채워지지 않아 어느 건물에서도 링크하지 않습니다.
  내용을 채운 뒤 `src/data/buildings.json` 의 해당 건물 `hotplaces` 에 추가하면 노출됩니다.

## version

- 1.0.0 출시
- 1.1.0 반응형 대응, 이미지 최적화, 빌드 스크립트 도입
- 1.2.0 UI 전면 리디자인, 캠퍼스맵 입체화
