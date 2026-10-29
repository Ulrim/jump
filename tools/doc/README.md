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

hwpx는 OWPML(KS X 6101) 구조를 직접 조립합니다. 한글이 설치된 PC에서
한 번 열어 확인한 뒤 배포하시기 바랍니다.
