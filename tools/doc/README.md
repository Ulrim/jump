# 확인 요청 문서 생성

협회에 보낼 「홈페이지 확인 요청 사항」 문서를 만드는 스크립트입니다.
내용은 `content.py` 한 곳에만 있고, hwpx와 docx가 같은 원본에서 생성됩니다.

```bash
# 내용 수정
vi tools/doc/content.py

# hwpx (표준 라이브러리만 사용)
python3 tools/doc/build_hwpx.py docs/전남한국줄넘기협회_홈페이지_확인요청사항.hwpx

# docx (docx npm 패키지 필요)
python3 -c "import sys;sys.path.insert(0,'tools/doc');import content as C,json;json.dump(
{'TITLE':C.TITLE,'SUBTITLE':C.SUBTITLE,'META':C.META,'INTRO':C.INTRO,'HOWTO':C.HOWTO,
 'SECTIONS':C.SECTIONS,'FILES':C.FILES_REQUESTED,'DECISIONS':C.DECISIONS,'CLOSING':C.CLOSING},
 open('/tmp/c.json','w'),ensure_ascii=False)"
node tools/doc/build_docx.js /tmp/c.json docs/전남한국줄넘기협회_홈페이지_확인요청사항.docx
```

## hwpx 구조 검증

```bash
python3 tools/doc/verify.py docs/전남한국줄넘기협회_홈페이지_확인요청사항.hwpx
```

패키지 규약(mimetype 선두·무압축), XML 적합성, 한컴 규약, 참조 무결성을 점검합니다.

### 한컴 규약 중 특히 틀리기 쉬운 것

1차 작성분이 한글에서 열리지 않았고, 원인은 아래였습니다. 수정 시 유지해야 합니다.

| 규칙 | 설명 |
|---|---|
| charPr 의 4형제 | `underline`·`strikeout`·`outline`·`shadow` 를 **항상** 출력. 값이 NONE 이어도 생략 불가 |
| paraPr margin | `<hh:margin><hh:intent value="0"/>…` — `hc:` 네임스페이스나 `unit` 속성을 쓰지 않음 |
| switch 미사용 | `hh:switch`/`hh:case` 를 쓰지 않고 `margin`·`lineSpacing` 을 직접 둠 |
| 풀 네임스페이스 | head·sec·package 루트에 14개 네임스페이스를 모두 선언 |
| linesegarray | 모든 `<hp:p>` 끝에 필요 |
| secPr 뒤 colPr | `<hp:ctrl><hp:colPr …/></hp:ctrl>` 가 secPr 바로 뒤에 와야 함 |
| hp:grid | `strtnum` 같은 비표준 속성을 넣으면 안 됨 |

한글이 설치된 PC에서 한 번 열어 확인한 뒤 배포하시기 바랍니다.
