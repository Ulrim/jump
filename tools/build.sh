#!/usr/bin/env bash
# 전남줄넘기협회 정적 사이트 빌드 스크립트
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

build index.html       ""            "전남 줄넘기의 모든 일정"        "전남줄넘기협회 공식 홈페이지. 대회 접수와 마감일, 지도자 연수, 자격증 발급, 전라남도 22개 시·군 등록 클럽 정보를 한곳에서 확인하세요."
build about.html       about         "협회소개"                      "전남줄넘기협회의 인사말, 미션과 비전, 연혁, 조직도와 임원 현황을 소개합니다."
build competition.html competition   "대회"                          "전남줄넘기협회 연간 대회 일정, 스피드·프리스타일·음악줄넘기 등 경기 종목과 규정, 참가 신청 안내."
build education.html   education     "교육 · 자격"                   "줄넘기 지도자 3급~1급, 심판 자격, 주니어 인증제 과정과 연수 일정, 자격증 발급·조회 안내."
build clubs.html       clubs         "시군지부 · 클럽"               "전라남도 22개 시·군 지부 현황과 등록 클럽 찾기, 지부·클럽 가입 절차를 안내합니다."
build news.html        news          "소식"                          "전남줄넘기협회 공지사항, 보도자료, 대회 요강 및 서식 자료실입니다."
build gallery.html     news          "갤러리"                        "전남줄넘기협회 대회와 연수, 행사 현장의 사진 기록입니다."
build contact.html     contact       "문의 · 오시는 길"              "전남줄넘기협회 사무국 위치와 연락처, 온라인 문의, 자주 묻는 질문을 확인하세요."

echo "done."
