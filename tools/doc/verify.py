# -*- coding: utf-8 -*-
import sys, zipfile, re
from xml.etree import ElementTree as ET

z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
ok = True
def chk(cond, msg):
    global ok
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond: ok = False

print("[패키지]")
chk(names[0] == "mimetype", "mimetype 이 첫 엔트리")
chk(z.getinfo("mimetype").compress_type == 0, "mimetype 무압축(STORED)")
chk(z.read("mimetype") == b"application/hwp+zip", "mimetype 내용")
for n in ["version.xml","settings.xml","META-INF/container.xml","META-INF/manifest.xml",
          "Contents/content.hpf","Contents/header.xml","Contents/section0.xml"]:
    chk(n in names, "필수 엔트리 %s" % n)
chk(z.testzip() is None, "ZIP 무결성")

print("\n[XML 적합성]")
for n in names:
    if n.endswith((".xml",".hpf")):
        try:
            ET.fromstring(z.read(n)); chk(True, n)
        except Exception as e:
            chk(False, "%s — %s" % (n, e))

hdr = z.read("Contents/header.xml").decode()
sec = z.read("Contents/section0.xml").decode()
hpf = z.read("Contents/content.hpf").decode()

print("\n[네임스페이스]")
for label, doc in [("header", hdr), ("section0", sec), ("content.hpf", hpf)]:
    chk('xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"' in doc
        and 'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"' in doc
        and 'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"' in doc,
        "%s 루트에 풀 네임스페이스" % label)

print("\n[한컴 규약]")
chk("hh:switch" not in hdr and "hp:switch" not in hdr, "paraPr 에 switch 미사용")
chk("<hc:" not in hdr, "header 에 hc: 요소 미사용(margin 은 hh:)")
n_char = hdr.count("<hh:charPr ")
chk(hdr.count("<hh:underline ") == n_char, "charPr %d개 전부 underline 포함" % n_char)
chk(hdr.count("<hh:strikeout ") == n_char, "charPr 전부 strikeout 포함")
chk(hdr.count("<hh:outline ") == n_char, "charPr 전부 outline 포함")
chk(hdr.count("<hh:shadow ") == n_char, "charPr 전부 shadow 포함")
chk(hdr.count('<hh:margin><hh:intent value=') == hdr.count("<hh:paraPr "), "paraPr margin 형식")
for tag in ["fontfaces","borderFills","charProperties","tabProperties","numberings","paraProperties","styles"]:
    chk(("<hh:%s" % tag) in hdr, "refList 에 %s" % tag)
pos = [hdr.find("<hh:%s" % t) for t in
       ["fontfaces","borderFills","charProperties","tabProperties","numberings","paraProperties","styles"]]
chk(pos == sorted(pos), "refList 자식 순서")

print("\n[본문]")
n_p = sec.count("<hp:p ")
chk(sec.count("<hp:linesegarray>") == n_p, "문단 %d개 전부 linesegarray" % n_p)
chk(sec.count("<hp:secPr ") == 1, "secPr 1개")
chk(sec.find("<hp:secPr") < sec.find("</hp:p>"), "secPr 이 첫 문단 안에")
chk("<hp:colPr " in sec, "secPr 뒤 ctrl/colPr")
chk('strtnum' not in sec, "hp:grid 에 비표준 속성 없음")

print("\n[참조 무결성]")
char_ids = set(re.findall(r'<hh:charPr id="(\d+)"', hdr))
para_ids = set(re.findall(r'<hh:paraPr id="(\d+)"', hdr))
used_c = set(re.findall(r'charPrIDRef="(\d+)"', sec))
used_p = set(re.findall(r'paraPrIDRef="(\d+)"', sec))
chk(used_c <= char_ids, "charPrIDRef 전부 정의됨 (쓰임 %s / 정의 %s)" % (sorted(used_c), sorted(char_ids)))
chk(used_p <= para_ids, "paraPrIDRef 전부 정의됨 (쓰임 %s / 정의 %s)" % (sorted(used_p), sorted(para_ids)))
bf = set(re.findall(r'<hh:borderFill id="(\d+)"', hdr))
chk(set(re.findall(r'borderFillIDRef="(\d+)"', hdr)) <= bf, "header borderFillIDRef 유효")
chk(set(re.findall(r'borderFillIDRef="(\d+)"', sec)) <= bf, "section borderFillIDRef 유효")
style_ids = set(re.findall(r'<hh:style id="(\d+)"', hdr))
chk(set(re.findall(r'styleIDRef="(\d+)"', sec)) <= style_ids, "styleIDRef 유효")
fonts = len(re.findall(r'<hh:font id="(\d+)"', hdr))
chk(fonts == 14, "fontface 7개 언어 x 2폰트 = %d" % fonts)
pids = re.findall(r'<hp:p id="(\d+)"', sec)
chk(len(pids) == len(set(pids)), "문단 id 고유 (%d개)" % len(pids))

print("\n결과:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
