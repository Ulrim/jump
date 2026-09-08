# 전남줄넘기협회 홈페이지

전라남도 줄넘기 종목단체(전남한국줄넘기협회)를 위한 **정적 웹사이트**입니다.
빌드 도구·프레임워크 없이 HTML / CSS / Vanilla JS만으로 제작되어, 어떤 정적 호스팅에도 그대로 올릴 수 있습니다.

> ⚠️ **데모 데이터 안내**
> 회장(양호찬), 대표 대회명, 개최 장소, 참가 규모, 전남 22개 시·군 구성 등은 공개된 보도자료와
> 관련 단체 자료를 바탕으로 조사한 내용입니다. 그 외 연락처·주소·일정·통계·기록·임원 명단은
> 사이트 구성을 위한 **예시 값**이므로 실제 오픈 전 협회 확인 후 교체해야 합니다.
> 조사 근거와 출처는 [`docs/RESEARCH.md`](docs/RESEARCH.md)에 정리되어 있습니다.

---

## 1. 빠르게 보기

```bash
# 저장소 루트에서
python3 -m http.server 8000
# 또는
npx http-server -p 8000
```
브라우저에서 `http://localhost:8000` 접속.

> `index.html`을 파일로 직접 열어도 동작하지만, 상대 경로 리소스 로딩을 위해 로컬 서버 사용을 권장합니다.

## 2. 페이지 구성

| 파일 | 메뉴 | 주요 섹션 |
|---|---|---|
| `index.html` | 메인 | 히어로 슬라이더 · 퀵메뉴 · 공지/보도/자료 탭 · 다가오는 일정 · 협회 통계 · 경기 종목 · 교육 안내 · 지부 · 갤러리 · CTA · 후원 롤링 |
| `about.html` | 협회소개 | 회장 인사말 · 미션/비전 · 연혁 · 조직도/임원 · CI · 정관 |
| `competition.html` | 대회 | 연간 대회일정 · 개인전/단체전 종목 · 경기 규정 · 참가 신청 · 기록실 |
| `education.html` | 교육 · 자격 | 지도자 3~1급 · 심판 · 주니어 인증제 · 연수 일정 · 자격증 조회 · FAQ |
| `clubs.html` | 시군지부 | 22개 시·군 지부 · 등록 클럽 찾기 · 가입 절차 · 학교스포츠클럽 지원 |
| `news.html` | 소식 | 공지사항 · 보도자료 · 자료실/서식 |
| `gallery.html` | 갤러리 | 분류 탭 기반 포토 갤러리 |
| `contact.html` | 문의 | 담당별 연락처 · 온라인 문의 폼 · 오시는 길 약도 · FAQ |

## 3. 디렉터리 구조

```
.
├── index.html … contact.html      생성된 정적 페이지 (배포 대상)
├── assets/
│   ├── css/style.css              디자인 시스템 + 전체 스타일
│   ├── js/main.js                 슬라이더 · 드로어 · 탭 · 아코디언 · 카운터 · 테마
│   └── img/favicon.svg
├── robots.txt / sitemap.xml
├── docs/RESEARCH.md               자료조사 결과 및 출처
└── tools/
    ├── build.sh                   페이지 조립 스크립트
    ├── partials/                  공통 head / header(GNB·드로어) / footer
    └── pages/*.body.html          각 페이지의 본문
```

## 4. 수정 방법

**본문만 고칠 때** — `index.html` 등 루트 HTML을 직접 편집해도 됩니다.

**헤더·푸터처럼 모든 페이지에 공통인 부분을 고칠 때** — `tools/partials/`를 수정한 뒤 재조립합니다.

```bash
bash tools/build.sh
```

`tools/build.sh`는 `tools/partials/head.html` + `header.html` + `tools/pages/<page>.body.html` + `footer.html`을
합쳐 루트에 HTML을 생성하고, 현재 페이지의 GNB 항목에 `aria-current="page"`를 자동으로 넣습니다.
빌드 결과물도 저장소에 커밋되므로 **배포 시 빌드는 필요 없습니다.**

## 5. 디자인 시스템

`assets/css/style.css` 상단의 CSS 커스텀 프로퍼티만 바꾸면 전체 톤을 일괄 변경할 수 있습니다.

| 토큰 | 값 | 의미 |
|---|---|---|
| `--navy-800` | `#0B1F3A` | 체육단체의 공신력을 나타내는 기본 색 |
| `--green-500` | `#00C36A` | 전라남도의 '청정·생명' 이미지 |
| `--lime-500` | `#C6FF00` | 줄넘기의 속도감·역동성 |
| `--orange-500` | `#FF6B2C` | 강조·알림 |

- 타이포그래피: Pretendard Variable (CDN) + 시스템 한글 폰트 폴백
- 라이트 / 다크 두 테마. `prefers-color-scheme`을 따르며 헤더의 토글로 수동 전환(`localStorage` 저장)
- 레이아웃 토큰: `--container`, `--gutter`, `--header-h`, `--util-h`

## 6. 구현된 UI/UX

- **히어로 슬라이더** — 자동재생 + 일시정지 버튼, 좌우 이동, 도트 이동, 마우스오버/포커스 시 정지, 탭 전환 시 정지, 좌우 방향키 지원, 비활성 슬라이드는 `tabindex="-1"`로 탭 순서에서 제외
- **메가 드롭다운 GNB**(≥1080px) / **슬라이드 드로어**(<1080px) — 포커스 트랩, ESC 닫기, 배경 스크롤 잠금
- **탭 · 아코디언** — WAI-ARIA 역할과 방향키(←/→/Home/End) 지원
- **스크롤 리빌 · 숫자 카운터** — `IntersectionObserver` 기반, `prefers-reduced-motion` 존중
- **폼** — 데모용 클라이언트 검증. 오류 시 첫 오류 항목으로 포커스 이동, `aria-live`로 결과 안내

## 7. 접근성 · SEO

- 페이지당 `<h1>` 1개, 건너뛰지 않는 제목 레벨
- 본문 바로가기 링크, 모든 아이콘 버튼에 `aria-label`, 모든 폼 컨트롤에 연결된 `<label>`
- 라이트·다크 모두 WCAG 2.1 AA 명도 대비(본문 4.5:1, 큰 글자 3:1) 충족 — 자동 스크립트로 전 페이지 검증
- 가로 스크롤 없음(430 / 768 / 1440px 검증), `prefers-reduced-motion` 대응, 인쇄 스타일 포함
- 페이지별 `<title>`·`description`·Open Graph 메타, `SportsOrganization` JSON-LD, `sitemap.xml`, `robots.txt`

## 8. 배포

정적 파일만 있으므로 GitHub Pages, Netlify, Vercel, Cloudflare Pages, 일반 웹호스팅 어디에나 업로드하면 됩니다.
GitHub Pages 사용 시 저장소 Settings → Pages에서 브랜치와 `/ (root)`를 지정하세요.

## 9. 오픈 전 체크리스트

- [ ] 사무국 주소 · 대표전화 · 팩스 · 이메일 실제 값으로 교체 (`tools/partials/footer.html`, `contact.html`)
- [ ] 임원 명단 및 창립 연도 등 연혁 확정 (`about.html`)
- [ ] 대회 일정 · 참가비 · 종목별 세부 규정을 최신 대회요강과 대조
- [ ] 자료실 파일 실제 업로드 및 링크 연결
- [ ] 갤러리 예시 그래픽을 실제 대회 사진으로 교체 (초상권 동의 확인)
- [ ] 도메인 확정 후 `sitemap.xml` · `robots.txt` · `canonical` · `og:url` 주소 갱신
- [ ] 공식 CI가 있다면 로고 SVG 교체 (`tools/partials/header.html`, `footer.html`, `assets/img/favicon.svg`)
- [ ] 개인정보처리방침 · 이용약관 실제 문서 연결

## 10. 라이선스 및 저작물

페이지의 모든 그래픽(로고, 히어로 배경, 카드 일러스트, 약도, 갤러리 이미지)은 이 저장소에서
직접 작성한 인라인 SVG입니다. 외부 사이트의 이미지·소스·서체 파일을 복제하지 않았습니다.
외부 의존성은 CDN으로 불러오는 Pretendard 웹폰트(SIL Open Font License) 하나뿐입니다.
