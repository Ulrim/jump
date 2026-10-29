# -*- coding: utf-8 -*-
"""OWPML(hwpx) 문서를 표준 라이브러리만으로 조립한다."""
import sys, os, zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C

XD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

# ---------- 글자 모양 (height = pt * 100) ----------
# id: (pt, bold, color, fontRef, spacing)
CHAR = {
    0:  (1000, 0, "#000000", 0),   # 본문
    1:  (2000, 1, "#111111", 1),   # 문서 제목
    2:  (1050, 0, "#555555", 0),   # 부제
    3:  (1400, 1, "#1A5E3A", 1),   # 장 제목
    4:  (1100, 1, "#111111", 1),   # 항목 제목
    5:  (950,  1, "#777777", 1),   # 라벨
    6:  (1000, 0, "#333333", 0),   # 설명
    7:  (1000, 0, "#999999", 0),   # 회신 밑줄
    8:  (1150, 1, "#111111", 1),   # 소제목
}
FACE = {0: "함초롬바탕", 1: "함초롬돋움"}

# ---------- 문단 모양 ----------
# id: (align, indentLeft, marginTop, marginBottom, lineSpacing)
PARA = {
    0: ("LEFT",   0,    0,   50, 160),   # 본문
    1: ("CENTER", 0,    0,  100, 160),   # 가운데
    2: ("LEFT", 2000,   0,   30, 160),   # 들여쓰기
    3: ("LEFT",   0,  600,  200, 160),   # 장 제목
    4: ("LEFT",   0,  300,   60, 160),   # 항목 제목
    5: ("LEFT", 1200,   0,  180, 160),   # 회신란
}

def xml_fontfaces():
    langs = ["HANGUL", "LATIN", "HANJA", "JAPANESE", "OTHER", "SYMBOL", "USER"]
    out = ['<hh:fontfaces itemCnt="%d">' % len(langs)]
    for lg in langs:
        out.append('<hh:fontface lang="%s" fontCnt="2">' % lg)
        for fid, nm in FACE.items():
            out.append(
                '<hh:font id="%d" face="%s" type="TTF" isEmbedded="0">'
                '<hh:typeInfo familyType="FCAT_GOTHIC" serifStyle="0" weight="0" proportion="0"'
                ' contrast="0" strokeVariation="0" armStyle="0" letterform="0" midline="0" xHeight="0"/>'
                '</hh:font>' % (fid, nm))
        out.append('</hh:fontface>')
    out.append('</hh:fontfaces>')
    return "".join(out)

def xml_charproperties():
    out = ['<hh:charProperties itemCnt="%d">' % len(CHAR)]
    for cid, (h, bold, color, fref) in sorted(CHAR.items()):
        out.append(
            '<hh:charPr id="%d" height="%d" textColor="%s" shadeColor="none"'
            ' useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="2">'
            '<hh:fontRef hangul="%d" latin="%d" hanja="%d" japanese="%d" other="%d" symbol="%d" user="%d"/>'
            '<hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
            '<hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
            '<hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
            '<hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
            % (cid, h, color, fref, fref, fref, fref, fref, fref, fref))
        if bold:
            out.append('<hh:bold/>')
        out.append('</hh:charPr>')
    out.append('</hh:charProperties>')
    return "".join(out)

def xml_paraproperties():
    out = ['<hh:paraProperties itemCnt="%d">' % len(PARA)]
    for pid, (align, indent, mtop, mbot, ls) in sorted(PARA.items()):
        out.append(
            '<hh:paraPr id="%d" tabPrIDRef="0" condense="0" fontLineHeight="0"'
            ' snapToGrid="1" suppressLineNumbers="0" checked="0">'
            '<hh:align horizontal="%s" vertical="BASELINE"/>'
            '<hh:heading type="NONE" idRef="0" level="0"/>'
            '<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD"'
            ' widowOrphan="0" keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK"/>'
            '<hh:autoSpacing eAsianEng="0" eAsianNum="0"/>'
            '<hh:switch><hh:case hp:required-namespace="http://www.hancom.co.kr/hwpml/2016/paragraph"'
            ' xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
            '<hh:margin><hc:intent value="0" unit="HWPUNIT"/><hc:left value="%d" unit="HWPUNIT"/>'
            '<hc:right value="0" unit="HWPUNIT"/><hc:prev value="%d" unit="HWPUNIT"/>'
            '<hc:next value="%d" unit="HWPUNIT"/></hh:margin>'
            '<hh:lineSpacing type="PERCENT" value="%d" unit="HWPUNIT"/></hh:case>'
            '<hh:default><hh:margin><hc:intent value="0" unit="HWPUNIT"/><hc:left value="%d" unit="HWPUNIT"/>'
            '<hc:right value="0" unit="HWPUNIT"/><hc:prev value="%d" unit="HWPUNIT"/>'
            '<hc:next value="%d" unit="HWPUNIT"/></hh:margin>'
            '<hh:lineSpacing type="PERCENT" value="%d" unit="HWPUNIT"/></hh:default></hh:switch>'
            '<hh:border borderFillIDRef="2" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0"'
            ' connect="0" ignoreMargin="0"/>'
            '</hh:paraPr>'
            % (pid, align, indent, mtop, mbot, ls, indent, mtop, mbot, ls))
    out.append('</hh:paraProperties>')
    return "".join(out)

def header_xml():
    return (XD +
        '<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"'
        ' xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"'
        ' xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"'
        ' version="1.31" secCnt="1">'
        '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
        '<hh:refList>'
        + xml_fontfaces() +
        '<hh:borderFills itemCnt="2">'
        '<hh:borderFill id="1" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
        '<hh:slash type="NONE" Crooked="0" isCounter="0"/>'
        '<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
        '<hh:leftBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:rightBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:topBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:bottomBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>'
        '</hh:borderFill>'
        '<hh:borderFill id="2" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
        '<hh:slash type="NONE" Crooked="0" isCounter="0"/>'
        '<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
        '<hh:leftBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:rightBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:topBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:bottomBorder type="NONE" width="0.1 mm" color="#000000"/>'
        '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>'
        '</hh:borderFill>'
        '</hh:borderFills>'
        + xml_charproperties() +
        '<hh:tabProperties itemCnt="1">'
        '<hh:tabPr id="0" autoTabLeft="0" autoTabRight="0"/>'
        '</hh:tabProperties>'
        '<hh:numberings itemCnt="1">'
        '<hh:numbering id="1" start="0">'
        + "".join(
            '<hh:paraHead start="1" level="%d" align="LEFT" useInstWidth="1" autoIndent="1"'
            ' widthAdjust="0" textOffsetType="PERCENT" textOffset="50" numFormat="DIGIT"'
            ' charPrIDRef="4294967295" checkable="0">^%d.</hh:paraHead>' % (i, i)
            for i in range(1, 8)) +
        '</hh:numbering>'
        '</hh:numberings>'
        + xml_paraproperties() +
        '<hh:styles itemCnt="1">'
        '<hh:style id="0" type="PARA" name="바탕글" engName="Normal" paraPrIDRef="0"'
        ' charPrIDRef="0" nextStyleIDRef="0" langID="1042" lockForm="0"/>'
        '</hh:styles>'
        '</hh:refList>'
        '<hh:compatibleDocument targetProgram="HWP201X"><hh:layoutCompatibility/></hh:compatibleDocument>'
        '</hh:head>')

# ---------- 본문 ----------
_pid = [0]
def para(text, para_id=0, char_id=0):
    _pid[0] += 1
    t = escape(text) if text else ""
    run = '<hp:run charPrIDRef="%d">%s</hp:run>' % (
        char_id, ('<hp:t>%s</hp:t>' % t) if t else '<hp:t/>')
    return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '%s</hp:p>' % (_pid[0], para_id, run))

def para_runs(parts, para_id=0):
    """parts = [(text, charId), ...] 한 문단 안에서 서식을 섞는다."""
    _pid[0] += 1
    runs = "".join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (c, escape(t))
                   for t, c in parts)
    return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '%s</hp:p>' % (_pid[0], para_id, runs))

def pagebreak():
    _pid[0] += 1
    return ('<hp:p id="%d" paraPrIDRef="0" styleIDRef="0" pageBreak="1" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p>' % _pid[0])

SECPR = (
    '<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000"'
    ' tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0"'
    ' textVerticalWidthHead="0" masterPageCnt="0">'
    '<hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0" strtnum="0"/>'
    '<hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>'
    '<hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0"'
    ' border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>'
    '<hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>'
    '<hp:pagePr landscape="WIDELY" width="59528" height="84188" gutterType="LEFT_ONLY">'
    '<hp:margin header="4252" footer="4252" gutter="0" left="7087" right="7087" top="5669" bottom="4252"/>'
    '</hp:pagePr>'
    '<hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
    '<hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/>'
    '<hp:noteSpacing betweenNotes="850" belowLine="567" aboveLine="850"/>'
    '<hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/>'
    '</hp:footNotePr>'
    '<hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
    '<hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/>'
    '<hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>'
    '<hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/>'
    '</hp:endNotePr>'
    '<hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0"'
    ' footerInside="0" fillArea="PAPER">'
    '<hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
    '<hp:pageBorderFill type="EVEN" borderFillIDRef="1" textBorder="PAPER" headerInside="0"'
    ' footerInside="0" fillArea="PAPER">'
    '<hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
    '<hp:pageBorderFill type="ODD" borderFillIDRef="1" textBorder="PAPER" headerInside="0"'
    ' footerInside="0" fillArea="PAPER">'
    '<hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
    '</hp:secPr>')

LINE = "─" * 44
BLANK_FILL = "ㅤ" * 1

def build_body():
    p = []
    # 첫 문단에 secPr 를 싣는다
    _pid[0] += 1
    p.append('<hp:p id="%d" paraPrIDRef="1" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
             '<hp:run charPrIDRef="1">%s<hp:t>%s</hp:t></hp:run></hp:p>'
             % (_pid[0], SECPR, escape(C.TITLE)))
    p.append(para(C.SUBTITLE, 1, 2))
    p.append(para("", 0, 0))

    # 문서 정보
    for k, v in C.META:
        p.append(para_runs([("%s  " % k, 5), (": %s" % v, 6)], 2))
    p.append(para("", 0, 0))
    p.append(para(LINE, 0, 7))
    p.append(para("", 0, 0))

    for t in C.INTRO:
        p.append(para(t, 0, 6))
    p.append(para("", 0, 0))

    p.append(para("작성 방법", 4, 8))
    for i, t in enumerate(C.HOWTO, 1):
        p.append(para("%d. %s" % (i, t), 2, 6))
    p.append(para("", 0, 0))

    # 본문 섹션
    for sec in C.SECTIONS:
        p.append(pagebreak())
        p.append(para("%s. %s" % (sec["no"], sec["title"]), 3, 3))
        p.append(para(sec["desc"], 0, 6))
        p.append(para(LINE, 0, 7))
        p.append(para("", 0, 0))
        for code, name, cur, ask in sec["items"]:
            p.append(para_runs([("[%s] " % code, 4), (name, 4)], 4))
            p.append(para_runs([("현재 표기  ", 5), (cur, 6)], 2))
            p.append(para_runs([("확인 요청  ", 5), (ask, 6)], 2))
            p.append(para_runs([("회      신  ", 5), ("_" * 52, 7)], 2))
            p.append(para("_" * 64, 5, 7))

    # 자료 요청
    p.append(pagebreak())
    p.append(para("4. 자료 요청 목록", 3, 3))
    p.append(para("아래 자료는 파일로 받아야 홈페이지에 반영할 수 있습니다. 보유하신 것만 주셔도 됩니다.", 0, 6))
    p.append(para(LINE, 0, 7))
    p.append(para("", 0, 0))
    for i, (nm, fmt, rel) in enumerate(C.FILES_REQUESTED, 1):
        p.append(para_runs([("%02d. " % i, 4), (nm, 4), ("   (관련 %s)" % rel, 5)], 4))
        p.append(para_runs([("형식  ", 5), (fmt, 6), ("        제공 가능 여부  □ 가능   □ 불가   □ 일부", 6)], 2))
        p.append(para("", 0, 0))

    # 의사결정
    p.append(pagebreak())
    p.append(para("5. 협회 결정이 필요한 사항", 3, 3))
    p.append(para("저희가 임의로 정할 수 없는 항목입니다. 방향만 정해 주시면 그에 맞춰 제작하겠습니다.", 0, 6))
    p.append(para(LINE, 0, 7))
    p.append(para("", 0, 0))
    for code, name, desc in C.DECISIONS:
        p.append(para_runs([("[%s] " % code, 4), (name, 4)], 4))
        p.append(para(desc, 2, 6))
        p.append(para_runs([("결      정  ", 5), ("_" * 52, 7)], 2))
        p.append(para("", 0, 0))

    # 맺음
    p.append(para("", 0, 0))
    p.append(para(LINE, 0, 7))
    for t in C.CLOSING:
        p.append(para(t, 0, 6))
    p.append(para("", 0, 0))
    p.append(para_runs([("담당  ", 5), ("                                        ", 7)], 2))
    p.append(para_runs([("연락처  ", 5), ("                                        ", 7)], 2))
    p.append(para_runs([("이메일  ", 5), ("                                        ", 7)], 2))
    return "".join(p)

def section_xml():
    return (XD +
        '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"'
        ' xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"'
        ' xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph"'
        ' xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">'
        + build_body() + '</hs:sec>')

def settings_xml():
    return (XD +
        '<ha:HWPApplicationSetting xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app">'
        '<ha:CaretPosition listIDRef="0" paraIDRef="0" pos="0"/>'
        '</ha:HWPApplicationSetting>')

def version_xml():
    return (XD +
        '<hv:HCFVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version"'
        ' tagetApplication="WORDPROCESSOR" major="5" minor="1" micro="1" buildNumber="0"'
        ' os="1" xmlVersion="1.4" application="Hancom Office Hangul"'
        ' appVersion="10, 0, 0, 0"/>')

def container_xml():
    return (XD +
        '<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container"'
        ' xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf">'
        '<ocf:rootfiles>'
        '<ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>'
        '</ocf:rootfiles></ocf:container>')

def manifest_xml():
    return (XD +
        '<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" version="1.2">'
        '<odf:file-entry odf:full-path="/" odf:media-type="application/hwp+zip"/>'
        '<odf:file-entry odf:full-path="Contents/header.xml" odf:media-type="application/xml"/>'
        '<odf:file-entry odf:full-path="Contents/section0.xml" odf:media-type="application/xml"/>'
        '<odf:file-entry odf:full-path="settings.xml" odf:media-type="application/xml"/>'
        '</odf:manifest>')

def container_rdf():
    return (XD +
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'
        ' xmlns:ns0="http://www.hancom.co.kr/hwpml/2011/rdf#">'
        '<rdf:Description rdf:about="">'
        '<ns0:hasPart rdf:resource="Contents/section0.xml"/>'
        '</rdf:Description></rdf:RDF>')

def content_hpf():
    return (XD +
        '<opf:package xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app"'
        ' version="" unique-identifier="" id="">'
        '<opf:metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<opf:title>%s</opf:title>'
        '<opf:language>ko</opf:language>'
        '<opf:meta name="creator" content=""/>'
        '<opf:meta name="subject" content=""/>'
        '<opf:meta name="description" content=""/>'
        '<opf:meta name="lastsaveby" content=""/>'
        '<opf:meta name="CreatedDate" content="2026-10-29"/>'
        '<opf:meta name="ModifiedDate" content="2026-10-29"/>'
        '</opf:metadata>'
        '<opf:manifest>'
        '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
        '<opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>'
        '<opf:item id="settings" href="settings.xml" media-type="application/xml"/>'
        '</opf:manifest>'
        '<opf:spine><opf:itemref idref="header" linear="yes"/>'
        '<opf:itemref idref="section0" linear="yes"/></opf:spine>'
        '</opf:package>' % escape(C.TITLE))

def prv_text():
    lines = [C.TITLE, C.SUBTITLE, ""]
    for sec in C.SECTIONS:
        lines.append("%s. %s" % (sec["no"], sec["title"]))
    return "\n".join(lines)

def main(out_path):
    files = [
        ("version.xml", version_xml()),
        ("META-INF/container.xml", container_xml()),
        ("META-INF/container.rdf", container_rdf()),
        ("META-INF/manifest.xml", manifest_xml()),
        ("Contents/content.hpf", content_hpf()),
        ("Contents/header.xml", header_xml()),
        ("Contents/section0.xml", section_xml()),
        ("settings.xml", settings_xml()),
        ("Preview/PrvText.txt", prv_text()),
    ]
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        # mimetype 은 반드시 첫 항목 + 무압축
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/hwp+zip")
        for name, data in files:
            z.writestr(name, data.encode("utf-8"))
    return out_path

if __name__ == "__main__":
    print(main(sys.argv[1]))
