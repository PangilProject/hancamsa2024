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
├── templates/        HTML 템플릿 - _ 로 시작하면 공통 조각
├── data/             페이지 내용 (JSON)
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

## 페이지 구성

- `index.html` — 메인 (히어로 캐러셀)
- `campusMap.html` — 캠퍼스 지도. 건물을 클릭하면 상세로 이동
- `introduce.html` — 사이트·개발자·과목 소개
- `html/*.html` — 건물 11곳
- `html/info/*.html` — 핫플레이스 47곳

## 반응형

브레이크포인트는 `src/assets/css/responsive.css` 한 곳에 모여 있습니다.

- ~1024px 태블릿 가로
- ~768px 태블릿 세로·큰 폰 — 가로 배치가 세로로 쌓이고, 사이드 메뉴가 하단 바로 바뀝니다
- ~480px 폰

캠퍼스맵의 `usemap` 좌표는 픽셀 고정값이라 이미지가 줄면 클릭 영역이 어긋납니다.
`src/assets/js/responsive.js` 가 실제 렌더 크기에 맞춰 좌표를 다시 계산합니다.
좁은 화면에서는 이미지맵 대신 건물 목록 버튼이 보입니다.

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
