#!/usr/bin/env bash
# 전남한국줄넘기협회 정적 사이트 빌드 스크립트
# 사용법: bash tools/build.sh
# tools/partials 의 공통 헤더/푸터와 tools/pages/*.body.html 을 합쳐 루트에 HTML을 생성합니다.
set -euo pipefail
cd "$(dirname "$0")/.."

HEAD="tools/partials/head.html"
HEADER="tools/partials/header.html"
FOOTER="tools/partials/footer.html"
NAV_KEYS=(about competition education clubs news contact)

build() {
  local file="$1" active="$2" title="$3" desc="$4"
  local body="tools/pages/${file%.html}.body.html"
  [ -f "$body" ] || { echo "missing $body" >&2; exit 1; }

  {
    sed -e "s|__TITLE__|${title}|g" -e "s|__DESC__|${desc}|g" -e "s|__FILE__|${file}|g" "$HEAD"

    local hdr
    hdr="$(cat "$HEADER")"
    for k in "${NAV_KEYS[@]}"; do
      if [ "$k" = "$active" ]; then
        hdr="${hdr//__NAV_${k}__/aria-current=\"page\"}"
      else
        hdr="${hdr//__NAV_${k}__/}"
      fi
    done
    printf '%s\n' "$hdr"

    cat "$body"
    cat "$FOOTER"
  } > "$file"
  echo "built  $file"
}

build index.html       ""            "전남 줄넘기의 모든 일정"        "전남한국줄넘기협회 공식 홈페이지. 2026 연간 일정과 경기 종목, 지도자 자격연수와 주니어 심사, 전라남도 12개 시·군 지부 정보를 한곳에서 확인하세요."
build about.html       about         "협회소개"                      "2014년 창립한 한국줄넘기협회 산하 전남지부입니다. 인사말과 미션·비전, 연혁, 조직도와 임원 현황, 공식 로고를 안내합니다."
build competition.html competition   "대회"                          "전남한국줄넘기협회 2026 연간 일정, 1종목·2종목 경기 종목과 30초 계측 규정, 참가비와 온라인 접수 안내."
build education.html   education     "교육 · 자격"                   "협회 연수원이 운영하는 지도자 자격연수(연 2회)와 주니어 심사(연 3회) 일정, 자격 발급 안내."
build clubs.html       clubs         "시군지부"                      "전라남도 12개 시·군 지부 현황과 지부 회장, 지부·클럽 가입 절차를 안내합니다."
build news.html        news          "소식"                          "전남한국줄넘기협회 공지와 2026 연간 일정, 자료실 안내입니다."
build gallery.html     news          "갤러리"                        "전남한국줄넘기협회 대회와 연수 현장의 사진 기록입니다."
build contact.html     contact       "문의 · 오시는 길"              "전남한국줄넘기협회 사무국 위치(순천시 조례동)와 연락처, 문의 방법과 자주 묻는 질문을 확인하세요."

echo "done."
