const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Header, Footer, AlignmentType, LevelFormat,
        WidthType, ShadingType, BorderStyle, PageNumber, HeadingLevel, PageBreak, VerticalAlign } = D;
const C = require("./content.js");
const UCS = require("./ucs.js");

const FONT = "Times New Roman", W = 9639;           // chiều rộng nội dung (DXA)
const IMG = "../img/";
const numbering = [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
  style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }];
let listId = 0;

// ---------- hàm tiện ích ----------
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 26, bold: o.bold, italics: o.italics, color: o.color });
function rich(text, o = {}) {                       // **đậm** trong chuỗi
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map(s => s.startsWith("**") ? run(s.slice(2, -2), { ...o, bold: true }) : run(s, o));
}
const P = (text, o = {}) => new Paragraph({ alignment: o.align, spacing: { after: o.after ?? 100, before: o.before ?? 0, line: 300 },
  indent: o.indent, keepNext: o.keepNext, children: rich(text, o) });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 360, after: 200 }, children: [run(t, { bold: true, size: 32 })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 280, after: 140 }, children: [run(t, { bold: true, size: 28 })] });
const H3 = (t) => new Paragraph({ keepNext: true, spacing: { before: 180, after: 100 }, children: [run(t, { bold: true, size: 26 })] });
const H4 = (t) => new Paragraph({ keepNext: true, spacing: { before: 120, after: 80 }, children: [run(t, { bold: true, italics: true, size: 26 })] });
const bullets = (arr) => arr.map(t => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 300 }, children: rich(t) }));
function steps(arr) {                               // danh sách đánh số, mỗi danh sách đánh lại từ 1
  const ref = "n" + (++listId);
  numbering.push({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 400 } } } }] });
  return arr.map(t => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 300 }, children: rich(t) }));
}
const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(text, w, o = {}) {
  const paras = (Array.isArray(text) ? text : [text]).map(t => new Paragraph({ alignment: o.align, spacing: { after: 40, line: 264 }, children: rich(String(t), { size: o.size || 22, bold: o.bold, color: o.color }) }));
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: paras });
}
function table(headers, rows, widths, o = {}) {
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, widths[i], { fill: "000000", color: "FFFFFF", bold: true })) });
  const body = rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], { fill: o.zebra && ri % 2 ? "F3F3F3" : undefined, bold: o.boldFirst && i === 0 })) }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [head, ...body] });
}
function image(file, wpx) {
  const buf = fs.readFileSync(IMG + file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);   // kích thước PNG
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 120 }, keepNext: false,
    children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: Math.round(wpx * h / w) },
      altText: { title: file, description: file, name: file } })] });
}
const spacer = () => new Paragraph({ spacing: { after: 60 }, children: [] });

// ---------- header / footer (giống Sample: bảng 2 hàng) ----------
function headerTable() {
  const wl = 7000, wr = 2639;
  const r = (a, b) => new TableRow({ children: [cell(a, wl, { size: 22 }), cell(b, wr, { size: 22 })] });
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [wl, wr],
    rows: [r("Hệ thống Đặt bàn Nhà hàng Hương Việt", "Phiên bản: 1.0"), r("Đặc tả hệ thống", "Ngày: 25/10/2026")] });
}
const header = () => new Header({ children: [headerTable(), new Paragraph({ spacing: { after: 0 }, children: [] })] });
const footer = () => new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
  run("Trang ", { size: 20 }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 }), run(" / ", { size: 20 }),
  new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 20 })] })] });

// ---------- nội dung ----------
const kids = [];
kids.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 120 }, children: [run("Đặc tả Hệ thống Đặt bàn Nhà hàng Hương Việt", { bold: true, size: 40 })] }));
kids.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [run("Version 1.0", { bold: true, size: 28 })] }));
kids.push(H3("Bảng ghi nhận thay đổi tài liệu"));
kids.push(table(["Ngày", "Phiên bản", "Mô tả", "Tác giả"],
  [["25/10/2026", "1.0", "Xây dựng tài liệu: mô tả hệ thống, glossary, business rules, đặc tả bổ sung, 14 use-case, mô hình dữ liệu, trạng thái lượt đặt, phân công và truy vết", "TV1 (BA)"]],
  [1500, 1300, 5339, 1500]));

kids.push(H1("I. Hệ thống đặt bàn Nhà hàng Hương Việt"));
kids.push(P("Nhà hàng Hương Việt cần xây dựng hệ thống đặt bàn trực tuyến nhằm tự động hóa việc tiếp nhận và quản lý chỗ ngồi, với một số tính năng cơ bản sau:"));
for (const [title, items] of C.desc) { kids.push(P("**" + title + "**", { keepNext: true, before: 80 })); kids.push(...bullets(items)); }

kids.push(H1("II. Bảng chú giải (Glossary)"));
kids.push(table(["STT", "Thuật ngữ", "Ý nghĩa"], C.glossary.map((g, i) => [String(i + 1), g[0], g[1]]), [700, 2700, 6239], { boldFirst: false }));

kids.push(H1("III. Quy tắc nghiệp vụ (Business Rules)"));
kids.push(P("Các quy tắc dưới đây được cài đặt tập trung ở tầng nghiệp vụ; các giá trị số (giờ, phút, ngày) có thể điều chỉnh trong tệp cấu hình."));
kids.push(table(["Mã", "Quy tắc", "Áp dụng cho"], C.rules, [900, 6839, 1900], { zebra: true }));

kids.push(H1("IV. Đặc tả bổ sung (Supplementary Specification)"));
for (const [t, d] of C.supp) { kids.push(H3(t)); kids.push(P(d)); }

kids.push(H1("V. Sơ đồ Use-Case"));
kids.push(H2("1. Sơ đồ tổng quan"));
kids.push(image("usecase_tongquan.png", 560));
kids.push(H3("1.1. Danh sách các Actor"));
kids.push(table(["STT", "Actor", "Ý nghĩa"], C.actors.map((a, i) => [String(i + 1), a[0] + " (" + a[1] + ")", a[2]]), [700, 2400, 6539]));
kids.push(H3("1.2. Danh sách các Use-case"));
kids.push(table(["STT", "Use-case", "Ý nghĩa", "Actor", "Phụ trách"],
  C.ucList.map((u, i) => [String(i + 1), u[0] + " " + u[1], u[2], u[3], u[4]]), [650, 2700, 3189, 1800, 1300], { zebra: true }));

UCS.forEach((u, i) => {
  const n = i + 2;
  kids.push(H2(`${n}. Use-case ${u.en} (${u.code} - ${u.vi})`));
  kids.push(H3(`${n}.1. Tóm tắt`)); kids.push(P(u.tomtat));
  kids.push(H3(`${n}.2. Dòng sự kiện`));
  kids.push(H4(`${n}.2.1. Dòng sự kiện chính`));
  kids.push(P(u.start, { keepNext: true }));
  kids.push(...steps(u.chinh));
  (u.sub || []).forEach(([t, s], k) => { kids.push(H4(`${n}.2.1.${k + 1}. ${t}`)); kids.push(...steps(s)); });
  kids.push(H4(`${n}.2.2. Các dòng sự kiện khác`));
  kids.push(...bullets(u.khac));
  kids.push(H3(`${n}.3. Các yêu cầu đặc biệt`)); kids.push(...(u.dacbiet[0] === "Không có" ? [P("Không có.")] : bullets(u.dacbiet)));
  kids.push(H3(`${n}.4. Trạng thái hệ thống trước khi bắt đầu thực hiện Use-case`)); kids.push(P(u.truoc));
  kids.push(H3(`${n}.5. Trạng thái hệ thống sau khi thực hiện Use-case`)); kids.push(P(u.sau));
  kids.push(H3(`${n}.6. Điểm mở rộng`)); kids.push(...(u.mo_rong[0] === "Không có" ? [P("Không có.")] : bullets(u.mo_rong)));
});

kids.push(H1("VI. Mô hình dữ liệu"));
kids.push(H2("1. Sơ đồ lớp (Class Diagram)"));
kids.push(image("sodo_lop.png", 400));
kids.push(P("Ghi chú: 1 khu vực có nhiều bàn; 1 bàn và 1 khách có nhiều lượt đặt; 1 lượt đặt có nhiều dòng nhật ký; mỗi dòng nhật ký có thể do 1 nhân viên thực hiện hoặc không (khách, hệ thống).", { italics: true, size: 24 }));
kids.push(H2("2. Từ điển dữ liệu (MySQL)"));
kids.push(table(["Bảng", "Cột", "Kiểu / ràng buộc", "Ý nghĩa"], C.dict, [1700, 2700, 2800, 2439]));

kids.push(H1("VII. Sơ đồ trạng thái của lượt đặt bàn"));
kids.push(image("sodo_trangthai.png", 470));
kids.push(P("Lượt đặt chỉ được đổi lịch hoặc hủy khi đang 'Đã xác nhận' và còn ít nhất 2 giờ (BR06); chỉ check-in trong khoảng -15 đến +15 phút quanh giờ đặt (BR07)."));

kids.push(H1("VIII. Phân công nhóm và truy vết"));
kids.push(H2("1. Phân công nhóm"));
kids.push(table(["Thành viên", "Vai trò", "Phụ trách"], C.team, [1400, 3000, 5239]));
kids.push(H2("2. Truy vết use-case với mã nguồn"));
kids.push(P("Bảng sau cho biết mỗi use-case được cài đặt ở đường dẫn web nào và hàm nghiệp vụ nào (tệp app/services.py), giúp đối chiếu đặc tả với chương trình."));
kids.push(table(["Use-case", "Đường dẫn web", "Hàm nghiệp vụ"], C.trace, [1200, 3800, 4639], { zebra: true }));

const doc = new Document({
  creator: "Nhóm SAD HK3", title: "Đặc tả Hệ thống Đặt bàn Nhà hàng Hương Việt",
  styles: { default: { document: { run: { font: FONT, size: 26 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 32, bold: true }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: numbering },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1900, bottom: 1000, left: 1417, right: 850, header: 500, footer: 400 } } },
    headers: { default: header() }, footers: { default: footer() }, children: kids }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("../Dac_ta_He_thong_Dat_ban_Huong_Viet.docx", b); console.log("ok", b.length); });
