const d = require('docx');
const fs = require('fs');
const {Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
       ShadingType, AlignmentType, HeadingLevel, BorderStyle, PageBreak} = d;
const C = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

const FONT = '맑은 고딕';
const W = 9360;                  // A4 usable width in DXA
const COL = [1700, W - 1700];
const GREY = 'F2F4F6', INK = '111111', MID = '555555', LINE = 'D0D5DB';
const bd = (c = LINE) => ({style: BorderStyle.SINGLE, size: 4, color: c});
const BORDERS = {top: bd(), bottom: bd(), left: bd(), right: bd(),
                 insideHorizontal: bd(), insideVertical: bd()};

const t = (text, o = {}) => new TextRun({text, font: FONT, size: o.size || 19,
  bold: !!o.bold, color: o.color || INK});
const p = (text, o = {}) => new Paragraph({
  children: Array.isArray(text) ? text : [t(text, o)],
  spacing: {before: o.before || 0, after: o.after === undefined ? 80 : o.after, line: 300},
  alignment: o.align, heading: o.heading, pageBreakBefore: o.pb,
  keepNext: !!o.keep, keepLines: !!o.keep});

const cell = (children, o = {}) => new TableCell({
  children: Array.isArray(children) ? children : [children],
  width: {size: o.w, type: WidthType.DXA},
  shading: o.fill ? {type: ShadingType.CLEAR, fill: o.fill, color: 'auto'} : undefined,
  margins: {top: 90, bottom: 90, left: 120, right: 120}});

const kvRow = (k, v, o = {}) => new TableRow({cantSplit: true, children: [
  cell(p(k, {size: 17, bold: true, color: MID, after: 0, keep: true}), {w: COL[0], fill: GREY}),
  cell(p(v, {size: 19, color: o.color || INK, after: 0, keep: true}), {w: COL[1]})]});

const blankRow = (k, lines = 2) => new TableRow({cantSplit: true, children: [
  cell(p(k, {size: 17, bold: true, color: MID, after: 0}), {w: COL[0], fill: GREY}),
  cell(Array.from({length: lines}, () => p('', {after: 0})), {w: COL[1]})]});

const itemTable = (rows) => new Table({
  columnWidths: COL, width: {size: W, type: WidthType.DXA}, borders: BORDERS, rows});

const body = [];

// ---- 표지 ----
body.push(p(C.TITLE, {size: 36, bold: true, align: AlignmentType.CENTER, after: 120, before: 600}));
body.push(p(C.SUBTITLE, {size: 19, color: MID, align: AlignmentType.CENTER, after: 500}));
body.push(new Table({columnWidths: COL, width: {size: W, type: WidthType.DXA}, borders: BORDERS,
  rows: C.META.map(([k, v]) => kvRow(k, v))}));
body.push(p('', {after: 400}));
C.INTRO.forEach(x => body.push(p(x, {color: '333333', after: 140})));
body.push(p('', {after: 200}));
body.push(p('작성 방법', {size: 22, bold: true, after: 140}));
C.HOWTO.forEach((x, i) => body.push(p(`${i + 1}.  ${x}`, {size: 19, color: '333333', after: 90})));

// ---- 확인 항목 ----
C.SECTIONS.forEach(sec => {
  body.push(p(`${sec.no}. ${sec.title}`, {size: 26, bold: true, color: '14593A', pb: true, after: 100}));
  body.push(p(sec.desc, {size: 18, color: MID, after: 240}));
  sec.items.forEach(([code, name, cur, ask]) => {
    body.push(itemTable([
      new TableRow({cantSplit: true, children: [
        cell(p(code, {size: 18, bold: true, color: '14593A', after: 0, keep: true}), {w: COL[0], fill: GREY}),
        cell(p(name, {size: 21, bold: true, after: 0, keep: true}), {w: COL[1], fill: GREY})]}),
      kvRow('현재 표기', cur, {color: MID}),
      kvRow('확인 요청', ask),
      blankRow('회신', 2)]));
    body.push(p('', {after: 180}));
  });
});

// ---- 자료 요청 ----
body.push(p('4. 자료 요청 목록', {size: 26, bold: true, color: '14593A', pb: true, after: 100}));
body.push(p('아래 자료는 파일로 받아야 홈페이지에 반영할 수 있습니다. 보유하신 것만 주셔도 됩니다.',
  {size: 18, color: MID, after: 240}));
const FC = [560, 2850, 2600, 1150, 2200];
body.push(new Table({columnWidths: FC, width: {size: W, type: WidthType.DXA}, borders: BORDERS,
  rows: [new TableRow({children: ['No', '자료명', '형식', '관련 항목', '제공 가능']
      .map((h, i) => cell(p(h, {size: 17, bold: true, color: MID, after: 0}), {w: FC[i], fill: GREY}))}),
    ...C.FILES.map(([nm, fmt, rel], i) => new TableRow({children: [
      cell(p(String(i + 1).padStart(2, '0'), {size: 18, after: 0}), {w: FC[0]}),
      cell(p(nm, {size: 19, bold: true, after: 0}), {w: FC[1]}),
      cell(p(fmt, {size: 18, color: MID, after: 0}), {w: FC[2]}),
      cell(p(rel, {size: 17, color: MID, after: 0}), {w: FC[3]}),
      cell(p('□ 가능    □ 불가', {size: 17, after: 0}), {w: FC[4]})]}))]}));

// ---- 의사결정 ----
body.push(p('5. 협회 결정이 필요한 사항', {size: 26, bold: true, color: '14593A', pb: true, after: 100}));
body.push(p('저희가 임의로 정할 수 없는 항목입니다. 방향만 정해 주시면 그에 맞춰 제작하겠습니다.',
  {size: 18, color: MID, after: 240}));
C.DECISIONS.forEach(([code, name, desc]) => {
  body.push(itemTable([
    new TableRow({cantSplit: true, children: [
      cell(p(code, {size: 18, bold: true, color: '14593A', after: 0, keep: true}), {w: COL[0], fill: GREY}),
      cell(p(name, {size: 21, bold: true, after: 0, keep: true}), {w: COL[1], fill: GREY})]}),
    kvRow('검토 사항', desc),
    blankRow('결정', 2)]));
  body.push(p('', {after: 180}));
});

// ---- 맺음 ----
body.push(p('', {after: 300}));
C.CLOSING.forEach(x => body.push(p(x, {size: 19, color: '333333', after: 110})));
body.push(p('', {after: 200}));
body.push(new Table({columnWidths: COL, width: {size: W, type: WidthType.DXA}, borders: BORDERS,
  rows: [blankRow('담당', 1), blankRow('연락처', 1), blankRow('이메일', 1)]}));

const doc = new Document({
  styles: {default: {document: {run: {font: FONT, size: 19, color: INK}}}},
  sections: [{properties: {page: {margin: {top: 1134, right: 1134, bottom: 1134, left: 1134}}},
              children: body}]});
Packer.toBuffer(doc).then(b => {fs.writeFileSync(process.argv[3], b); console.log('ok', b.length);});
