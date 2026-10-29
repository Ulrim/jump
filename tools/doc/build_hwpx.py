# -*- coding: utf-8 -*-
"""OWPML(hwpx) 생성 — 한컴 정상 출력 구조를 그대로 따른다. 표준 라이브러리만 사용."""
import sys, os, zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C

XD  = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
XD2 = '<?xml version="1.0" encoding="UTF-8"?>\n'
NS_HA = "http://www.hancom.co.kr/hwpml/2011/app"

# head / sec / package 루트가 공유하는 풀 네임스페이스 선언
OWPML_NS = (
    'xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
    'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
    'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" '
    'xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
    'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:opf="http://www.idpf.org/2007/opf/" '
    'xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
    'xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" '
    'xmlns:epub="http://www.idpf.org/2007/ops" '
    'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"')

LINESEG = ('<hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="1000"'
           ' textheight="1000" baseline="850" spacing="600" horzpos="0"'
           ' horzsize="45354" flags="393216"/></hp:linesegarray>')

FONTS = ["함초롬바탕", "함초롬돋움"]
LANGS = ["HANGUL", "LATIN", "HANJA", "JAPANESE", "OTHER", "SYMBOL", "USER"]

# id: (height, bold, color, fontIdx)
CHAR = {
    0: (1000, 0, "#000000", 0),   # 본문
    1: (2000, 1, "#111111", 1),   # 문서 제목
    2: (1000, 0, "#555555", 0),   # 부제
    3: (1400, 1, "#14593A", 1),   # 장 제목
    4: (1100, 1, "#111111", 1),   # 항목 제목
    5: (900,  1, "#777777", 1),   # 라벨
    6: (1000, 0, "#333333", 0),   # 설명
    7: (1000, 0, "#AAAAAA", 0),   # 괘선
    8: (1150, 1, "#111111", 1),   # 소제목
}
# id: (align, left, prev, next)
PARA = {
    0: ("LEFT",      0,   0,  60),
    1: ("CENTER",    0,   0, 120),
    2: ("LEFT",   2200,   0,  40),
    3: ("LEFT",      0, 700, 240),
    4: ("LEFT",      0, 360,  70),
    5: ("LEFT",   1400,   0, 220),
}

def fontfaces():
    out = ['<hh:fontfaces itemCnt="%d">' % len(LANGS)]
    for lg in LANGS:
        out.append('<hh:fontface lang="%s" fontCnt="%d">' % (lg, len(FONTS)))
        for i, nm in enumerate(FONTS):
            out.append('<hh:font id="%d" face="%s" type="TTF" isEmbedded="0"/>' % (i, nm))
        out.append('</hh:fontface>')
    out.append('</hh:fontfaces>')
    return "".join(out)

def charprops():
    out = ['<hh:charProperties itemCnt="%d">' % len(CHAR)]
    for cid, (h, bold, color, f) in sorted(CHAR.items()):
        out.append(
            '<hh:charPr id="%d" height="%d" textColor="%s" shadeColor="none"'
            ' useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="0">'
            '<hh:fontRef hangul="%d" latin="%d" hanja="%d" japanese="%d" other="%d" symbol="%d" user="%d"/>'
            '<hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
            '<hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
            '<hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
            '<hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
            % ((cid, h, color) + (f,) * 7))
        if bold:
            out.append('<hh:bold/>')
        # 한컴은 아래 넷을 항상 출력한다
        out.append('<hh:underline type="NONE" shape="SOLID" color="#000000"/>'
                   '<hh:strikeout shape="NONE" color="#000000"/>'
                   '<hh:outline type="NONE"/>'
                   '<hh:shadow type="NONE" color="#C0C0C0" offsetX="10" offsetY="10"/>')
        out.append('</hh:charPr>')
    out.append('</hh:charProperties>')
    return "".join(out)

def paraprops():
    out = ['<hh:paraProperties itemCnt="%d">' % len(PARA)]
    for pid, (align, left, prev, nxt) in sorted(PARA.items()):
        out.append(
            '<hh:paraPr id="%d" tabPrIDRef="0" condense="0" fontLineHeight="0"'
            ' snapToGrid="0" suppressLineNumbers="0" checked="0">'
            '<hh:align horizontal="%s" vertical="BASELINE"/>'
            '<hh:heading type="NONE" idRef="0" level="0"/>'
            '<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD"'
            ' widowOrphan="0" keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK"/>'
            '<hh:margin><hh:intent value="0"/><hh:left value="%d"/><hh:right value="0"/>'
            '<hh:prev value="%d"/><hh:next value="%d"/></hh:margin>'
            '<hh:lineSpacing type="PERCENT" value="165"/>'
            '</hh:paraPr>' % (pid, align, left, prev, nxt))
    out.append('</hh:paraProperties>')
    return "".join(out)

def header_xml():
    return (XD +
        '<hh:head %s version="1.5" secCnt="1">' % OWPML_NS +
        '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
        '<hh:refList>'
        + fontfaces() +
        '<hh:borderFills itemCnt="1">'
        '<hh:borderFill id="0" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
        '<hh:slash type="NONE" Crooked="0" isCounter="0"/>'
        '<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
        '<hh:leftBorder type="SOLID" width="0.1 mm" color="#000000"/>'
        '<hh:rightBorder type="SOLID" width="0.1 mm" color="#000000"/>'
        '<hh:topBorder type="SOLID" width="0.1 mm" color="#000000"/>'
        '<hh:bottomBorder type="SOLID" width="0.1 mm" color="#000000"/>'
        '<hh:diagonal type="NONE" width="0.1 mm" color="#000000"/>'
        '</hh:borderFill>'
        '</hh:borderFills>'
        + charprops() +
        '<hh:tabProperties itemCnt="1">'
        '<hh:tabPr id="0" autoTabLeft="1" autoTabRight="1"><hh:items itemCnt="0"/></hh:tabPr>'
        '</hh:tabProperties>'
        '<hh:numberings itemCnt="1">'
        '<hh:numbering id="0" start="1">'
        '<hh:paraHead level="1" start="1" numFormat="^1." textOffsetType="PERCENT"'
        ' textOffset="50" numberingChar="false" charPrIDRef="0">'
        '<hh:autoNumberFormat type="DIGIT" userChar="" prefixChar="" suffixChar="."/>'
        '</hh:paraHead>'
        '</hh:numbering>'
        '</hh:numberings>'
        + paraprops() +
        '<hh:styles itemCnt="1">'
        '<hh:style id="0" type="PARA" name="바탕글" engName="Normal" paraPrIDRef="0"'
        ' charPrIDRef="0" nextStyleIDRef="0" langID="1042" lockForm="0"/>'
        '</hh:styles>'
        '</hh:refList>'
        '</hh:head>')

SECPR = (
    '<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000"'
    ' tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0"'
    ' textVerticalWidthHead="0" masterPageCnt="0">'
    '<hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>'
    '<hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>'
    '<hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0"'
    ' border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>'
    '<hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>'
    '<hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY">'
    '<hp:margin header="4252" footer="4252" gutter="0" left="7087" right="7087" top="5668" bottom="4252"/>'
    '</hp:pagePr>'
    '<hp:footNotePr>'
    '<hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
    '<hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/>'
    '<hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/>'
    '<hp:numbering type="CONTINUOUS" newNum="1"/>'
    '<hp:placement place="EACH_COLUMN" beneathText="0"/>'
    '</hp:footNotePr>'
    '<hp:endNotePr>'
    '<hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
    '<hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/>'
    '<hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>'
    '<hp:numbering type="CONTINUOUS" newNum="1"/>'
    '<hp:placement place="END_OF_DOCUMENT" beneathText="0"/>'
    '</hp:endNotePr>'
    '<hp:pageBorderFill type="BOTH" borderFillIDRef="0" textBorder="PAPER" headerInside="0"'
    ' footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
    '<hp:pageBorderFill type="EVEN" borderFillIDRef="0" textBorder="PAPER" headerInside="0"'
    ' footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
    '<hp:pageBorderFill type="ODD" borderFillIDRef="0" textBorder="PAPER" headerInside="0"'
    ' footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
    '</hp:secPr>'
    '<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl>')

_pid = [0]
def _p(runs_xml, para_id, page_break=0):
    _pid[0] += 1
    return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="%d" columnBreak="0" merged="0">'
            '%s%s</hp:p>' % (_pid[0], para_id, page_break, runs_xml, LINESEG))

def para(text, para_id=0, char_id=0, pb=0):
    body = '<hp:t>%s</hp:t>' % escape(text) if text else '<hp:t/>'
    return _p('<hp:run charPrIDRef="%d">%s</hp:run>' % (char_id, body), para_id, pb)

def para_runs(parts, para_id=0, pb=0):
    runs = "".join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (c, escape(t))
                   for t, c in parts)
    return _p(runs, para_id, pb)

def first_para(text, para_id, char_id):
    _pid[0] += 1
    return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="%d">%s<hp:t>%s</hp:t></hp:run>%s</hp:p>'
            % (_pid[0], para_id, char_id, SECPR, escape(text), LINESEG))

RULE = "─" * 42

def build_body():
    p = [first_para(C.TITLE, 1, 1)]
    p.append(para(C.SUBTITLE, 1, 2))
    p.append(para("", 0, 0))
    for k, v in C.META:
        p.append(para_runs([("%s  :  " % k, 5), (v, 6)], 2))
    p.append(para("", 0, 0))
    p.append(para(RULE, 0, 7))
    for t in C.INTRO:
        p.append(para(t, 0, 6))
    p.append(para("", 0, 0))
    p.append(para("작성 방법", 4, 8))
    for i, t in enumerate(C.HOWTO, 1):
        p.append(para("%d.  %s" % (i, t), 2, 6))

    for sec in C.SECTIONS:
        p.append(para("%s. %s" % (sec["no"], sec["title"]), 3, 3, pb=1))
        p.append(para(sec["desc"], 0, 6))
        p.append(para(RULE, 0, 7))
        for code, name, cur, ask in sec["items"]:
            p.append(para_runs([("[%s]  " % code, 4), (name, 4)], 4))
            p.append(para_runs([("현재 표기  ", 5), (cur, 6)], 2))
            p.append(para_runs([("확인 요청  ", 5), (ask, 6)], 2))
            p.append(para_runs([("회      신  ", 5), ("_" * 50, 7)], 2))
            p.append(para("_" * 62, 5, 7))

    p.append(para("4. 자료 요청 목록", 3, 3, pb=1))
    p.append(para("아래 자료는 파일로 받아야 홈페이지에 반영할 수 있습니다. 보유하신 것만 주셔도 됩니다.", 0, 6))
    p.append(para(RULE, 0, 7))
    for i, (nm, fmt, rel) in enumerate(C.FILES_REQUESTED, 1):
        p.append(para_runs([("%02d.  " % i, 4), (nm, 4), ("     (관련 %s)" % rel, 5)], 4))
        p.append(para_runs([("형식  ", 5), (fmt, 6)], 2))
        p.append(para_runs([("제공 가능 여부  ", 5), ("□ 가능      □ 불가      □ 일부", 6)], 2))
        p.append(para("", 0, 0))

    p.append(para("5. 협회 결정이 필요한 사항", 3, 3, pb=1))
    p.append(para("저희가 임의로 정할 수 없는 항목입니다. 방향만 정해 주시면 그에 맞춰 제작하겠습니다.", 0, 6))
    p.append(para(RULE, 0, 7))
    for code, name, desc in C.DECISIONS:
        p.append(para_runs([("[%s]  " % code, 4), (name, 4)], 4))
        p.append(para(desc, 2, 6))
        p.append(para_runs([("결      정  ", 5), ("_" * 50, 7)], 2))
        p.append(para("", 0, 0))

    p.append(para("", 0, 0))
    p.append(para(RULE, 0, 7))
    for t in C.CLOSING:
        p.append(para(t, 0, 6))
    p.append(para("", 0, 0))
    for lbl in ("담당", "연락처", "이메일"):
        p.append(para_runs([("%s  " % lbl, 5), ("_" * 44, 7)], 2))
    return "".join(p)

def section_xml():
    return XD + '<hs:sec %s>' % OWPML_NS + build_body() + '</hs:sec>'

def main(out_path):
    files = [
        ("version.xml", XD2 +
            '<ha:HCFVersion xmlns:ha="%s" ha:targetApplication="WORDPROCESSOR"'
            ' ha:major="5" ha:minor="0" ha:micro="6" ha:buildNumber="0"/>' % NS_HA),
        ("META-INF/container.xml", XD2 +
            '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="Contents/content.hpf"'
            ' media-type="application/hwpml-package+xml"/></rootfiles></container>'),
        ("META-INF/manifest.xml", XD2 +
            '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
            '<manifest:file-entry manifest:full-path="/" manifest:media-type="application/hwpml-package+xml"/>'
            '<manifest:file-entry manifest:full-path="version.xml" manifest:media-type="application/xml"/>'
            '<manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="application/xml"/>'
            '<manifest:file-entry manifest:full-path="Contents/content.hpf" manifest:media-type="application/hwpml-package+xml"/>'
            '<manifest:file-entry manifest:full-path="Contents/header.xml" manifest:media-type="application/xml"/>'
            '<manifest:file-entry manifest:full-path="Contents/section0.xml" manifest:media-type="application/xml"/>'
            '</manifest:manifest>'),
        ("settings.xml", XD2 +
            '<ha:HWPApplicationSetting xmlns:ha="%s">'
            '<ha:CaretPosition ha:listIDRef="0" ha:paraIDRef="0" ha:pos="0"/>'
            '</ha:HWPApplicationSetting>' % NS_HA),
        ("Contents/content.hpf", XD +
            '<opf:package %s version="" unique-identifier="" id="">'
            '<opf:metadata>'
            '<dc:title>%s</dc:title><dc:creator></dc:creator>'
            '<dc:format>application/hwpml-package+xml</dc:format>'
            '</opf:metadata>'
            '<opf:manifest>'
            '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
            '<opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>'
            '<opf:item id="settings" href="settings.xml" media-type="application/xml"/>'
            '</opf:manifest>'
            '<opf:spine><opf:itemref idref="header" linear="yes"/>'
            '<opf:itemref idref="section0" linear="yes"/></opf:spine>'
            '</opf:package>' % (OWPML_NS, escape(C.TITLE))),
        ("Contents/header.xml", header_xml()),
        ("Contents/section0.xml", section_xml()),
    ]
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/hwp+zip")
        for name, data in files:
            z.writestr(name, data.encode("utf-8"))
    return out_path

if __name__ == "__main__":
    print(main(sys.argv[1]))
