import os
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_SETS = [
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
    ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
]
for reg, bold in FONT_SETS:
    if os.path.exists(reg) and os.path.exists(bold):
        pdfmetrics.registerFont(TTFont('R', reg, asciiReadable=True))
        pdfmetrics.registerFont(TTFont('B', bold, asciiReadable=True))
        break
else:
    raise RuntimeError('Не найден шрифт с кириллицей.')

WHITE = HexColor('#E8E6E1')
DIM = HexColor('#9AA0A6')
ACCENT = HexColor('#E0A030')
BG = HexColor('#0D0F12')
LINE = HexColor('#2A2E35')

def generate_pdf(data: dict, output_path: str) -> None:
    def st(name, **kw):
        return ParagraphStyle(name, fontName=kw.pop('f', 'R'), fontSize=kw.pop('s', 10),
                              leading=kw.pop('ld', 14), textColor=kw.pop('c', WHITE), **kw)

    h2_style = st('h', f='B', s=9, c=ACCENT, spaceAfter=4, ld=12)
    h3_style = st('h3', f='B', s=11, ld=14, spaceBefore=6)
    date_style = st('d', c=DIM, s=9, ld=12, alignment=2)
    co_style = st('co', c=DIM, s=9, ld=12, spaceAfter=4)
    body_style = st('b', s=10, ld=14)
    bullet_style = st('bul', s=10, ld=14, leftIndent=10, bulletIndent=0, spaceBefore=2)
    small_style = st('s', c=DIM, s=9, ld=12)

    def head(t):
        return [Paragraph(t.upper(), h2_style), HRFlowable(width='100%', thickness=.5, color=LINE, spaceAfter=6)]

    story = []
    
    # Шапка
    story.append(Paragraph(escape(data.get('name', '')), st('n', f='B', s=22, ld=26, c=WHITE)))
    story.append(Paragraph(escape(data.get('position', '')), st('r', c=DIM, s=11, ld=14, spaceBefore=2)))
    
    contacts = []
    if data.get('contact_email'): 
        # Делаем email кликабельным
        contacts.append(f"<a href='mailto:{data['contact_email']}' color='#9AA0A6'><u>{data['contact_email']}</u></a>")
    if data.get('contact_telegram'): 
        # Делаем TG кликабельным (с подчеркиванием)
        contacts.append(f"<a href='https://t.me/{data['contact_telegram']}' color='#9AA0A6'><u>t.me/{data['contact_telegram']}</u></a>")
    if data.get('contact_github'): 
        # Делаем GitHub кликабельным (с подчеркиванием)
        contacts.append(f"<a href='https://github.com/{data['contact_github']}' color='#9AA0A6'><u>github.com/{data['contact_github']}</u></a>")
    
    story.append(Paragraph(" | ".join(contacts), st('c', c=DIM, s=9, spaceBefore=6)))
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT, spaceAfter=0))
    story.append(Spacer(1, 10))

    # О себе
    if data.get('about'):
        story += head('О себе')
        story.append(Paragraph(escape(data['about']).replace('\n', '<br/>'), body_style))
        story.append(Spacer(1, 10))

    # Колонки
    left_col = []
    right_col = []

    exp = data.get('experience', [])
    if exp:
        left_col += head('Опыт работы')
        for i, job in enumerate(exp):
            if i > 0: left_col.append(Spacer(1, 8))
            row = Table([[Paragraph(escape(job.get('role', '')), h3_style),
                          Paragraph(escape(job.get('dates', '')), date_style)]],
                        colWidths=[None, 35 * mm])
            row.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                     ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
            left_col.append(row)
            left_col.append(Paragraph(escape(job.get('company', '')), co_style))
            for bullet in job.get('bullets', []):
                left_col.append(Paragraph(escape(bullet), bullet_style, bulletText='–'))

    skills = data.get('skills', [])
    if skills:
        right_col += head('Навыки')
        unique_skills = list(dict.fromkeys([s.strip() for s in skills if s.strip()]))
        right_col.append(Paragraph(", ".join(unique_skills), body_style))
        right_col.append(Spacer(1, 10))

    edu = data.get('education', [])
    if edu:
        right_col += head('Образование')
        for e in edu:
            right_col.append(Paragraph(escape(e.get('institution', '')), h3_style))
            right_col.append(Paragraph(escape(e.get('degree', '')), body_style))
            right_col.append(Paragraph(escape(e.get('dates', '')), small_style))
            right_col.append(Spacer(1, 6))

    courses = data.get('courses', [])
    if courses:
        right_col += head('Курсы')
        for c in courses:
            right_col.append(Paragraph(escape(c.get('name', '')), body_style))
            right_col.append(Paragraph(escape(c.get('provider', '')), small_style))
            right_col.append(Spacer(1, 4))

    if left_col or right_col:
        W = A4[0] - 30 * mm
        body_t = Table([[left_col, right_col]], colWidths=[W * 0.65 - 5*mm, W * 0.35 - 5*mm], hAlign='LEFT')
        body_t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                    ('RIGHTPADDING', (0, 0), (0, 0), 10),
                                    ('RIGHTPADDING', (1, 0), (1, 0), 0),
                                    ('TOPPADDING', (0, 0), (-1, -1), 0)]))
        story.append(body_t)

    def _dark_bg(canvas, doc_):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        canvas.restoreState()

    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title=data.get('name', 'Resume'))
    doc.build(story, onFirstPage=_dark_bg, onLaterPages=_dark_bg)