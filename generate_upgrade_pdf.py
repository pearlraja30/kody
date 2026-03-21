#!/usr/bin/env python3
"""Generate professional PDF for Kodys Technology Upgrade Assessment."""
from fpdf import FPDF
import os

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'Kodys_Technology_Upgrade_Assessment.pdf')


class UpgradePDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 5, 'Kodys Medical - Technology Upgrade Assessment', align='C')
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Confidential | Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, num, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(15, 52, 96)
        self.cell(0, 12, f'{num}. {title}', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(15, 52, 96)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def sub_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(22, 33, 62)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def alert_box(self, text, color='red'):
        colors = {
            'red':    (233, 69, 96),
            'yellow': (255, 193, 7),
            'green':  (46, 204, 113),
            'blue':   (52, 152, 219)
        }
        r, g, b = colors.get(color, colors['red'])
        self.set_fill_color(255, 245, 245) if color == 'red' else self.set_fill_color(245, 250, 255)
        self.set_draw_color(r, g, b)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, self.w - self.l_margin - self.r_margin, 18, style='DF')
        self.set_xy(x + 3, y + 2)
        self.set_draw_color(r, g, b)
        self.line(x, y, x, y + 18)
        self.line(x + 1, y, x + 1, y + 18)
        self.line(x + 2, y, x + 2, y + 18)
        self.set_xy(x + 6, y + 3)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(r, g, b)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 6, text)
        self.ln(6)

    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [(self.w - self.l_margin - self.r_margin) / len(headers)] * len(headers)

        # Header
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(15, 52, 96)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, fill=True, align='C')
        self.ln()

        # Rows
        self.set_font('Helvetica', '', 9)
        self.set_text_color(40, 40, 40)
        for ri, row in enumerate(rows):
            fill = ri % 2 == 0
            self.set_fill_color(248, 249, 255) if fill else self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, fill=fill)
            self.ln()
        self.ln(4)


def generate():
    pdf = UpgradePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ─── COVER PAGE ───
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font('Helvetica', 'B', 32)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 15, 'Kodys Medical Platform', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 20)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 12, 'Technology Upgrade Assessment', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    pdf.set_draw_color(15, 52, 96)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, 'Prepared for: Client Review', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Date: 21 March 2026', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, 'Version: 1.0', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(25)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 8, 'CONFIDENTIAL - For Internal Use Only', align='C', new_x='LMARGIN', new_y='NEXT')

    # ─── SECTION 1: Why Upgrade ───
    pdf.add_page()
    pdf.section_title('1', 'Why Upgrade Is Critical')
    pdf.body_text(
        'The Kodys Medical application currently runs on Python 2.7 and Django 1.11, '
        'both of which reached End-of-Life (EOL) status over 6 years ago. '
        'This means no security patches, no bug fixes, and no compatibility updates.'
    )
    pdf.add_table(
        ['Component', 'Version', 'EOL Date', 'Years Since EOL'],
        [
            ['Python', '2.7.18', '1 Jan 2020', '6+ years'],
            ['Django', '1.11.29', '1 Apr 2020', '6+ years'],
            ['NumPy', '1.16.6', 'Jan 2020', '6+ years'],
            ['SciPy', '1.2.3', 'Jan 2020', '6+ years'],
        ],
        [45, 45, 45, 45]
    )
    pdf.alert_box('WARNING: Any newly discovered vulnerability will remain unpatched indefinitely.')

    # ─── SECTION 2: Security Risks ───
    pdf.section_title('2', 'Security & Compliance Risks')
    pdf.sub_title('2.1 Security Vulnerabilities')
    pdf.add_table(
        ['Risk', 'Severity', 'Impact'],
        [
            ['No Python security patches', 'CRITICAL', 'Known CVEs remain unpatched'],
            ['No Django security updates', 'CRITICAL', 'CSRF, XSS, SQL injection exposure'],
            ['Outdated cryptography (v2.9)', 'CRITICAL', 'Weak encryption for patient data'],
            ['No TLS 1.3 support', 'HIGH', 'Older SSL/TLS weaknesses'],
        ],
        [55, 30, 95]
    )
    pdf.sub_title('2.2 Compliance Concerns')
    pdf.add_table(
        ['Standard', 'Requirement', 'Status'],
        [
            ['HIPAA', 'Use supported/patched software', 'NON-COMPLIANT'],
            ['ISO 27001', 'Regular security updates', 'NON-COMPLIANT'],
            ['FDA 21 CFR Part 11', 'Validated, maintained systems', 'AT RISK'],
            ['IEC 62304', 'Medical device software lifecycle', 'AT RISK'],
        ],
        [50, 65, 65]
    )

    # ─── SECTION 3: Dependency Chain ───
    pdf.add_page()
    pdf.section_title('3', 'Dependency Chain Analysis')
    pdf.body_text(
        'Every library depends on others. Python version dictates which versions of ALL '
        'libraries are available. You cannot upgrade just one library independently.'
    )
    pdf.add_table(
        ['Library', 'Current (Py2.7)', 'Target (Py3.12)', 'Migration Notes'],
        [
            ['Django', '1.11.29', '4.2 LTS', 'Major rewrite required'],
            ['NumPy', '1.16.6', '1.26.x', 'Minor deprecations'],
            ['SciPy', '1.2.3', '1.12.x', 'Compatible'],
            ['Pandas', '0.24.2', '2.1.x', '.append() removed'],
            ['Matplotlib', '2.2.5', '3.8.x', 'API renames'],
            ['OpenCV', '4.2.0', '4.9.x', 'Compatible'],
            ['Cryptography', '2.9.2', '42.x', 'Major API changes'],
            ['Pillow', '6.2.2', '10.x', 'Compatible'],
            ['scikit-learn', '0.20.4', '1.4.x', 'API changes'],
            ['biosppy', '0.6.1', '2.2.1', 'Mostly compatible'],
            ['heartpy', '1.2.7', '1.2.7', 'Should work'],
            ['pyhrv', '0.4.1', '0.4.1', 'May need patching'],
        ],
        [35, 35, 35, 75]
    )

    # ─── SECTION 4: What Happens If We Don't ───
    pdf.section_title('4', 'What Happens If We Don\'t Upgrade')
    pdf.add_table(
        ['Timeline', 'Risk', 'Consequence'],
        [
            ['Now', 'Running on 6yr EOL stack', 'Acceptable for short-term testing'],
            ['6 months', 'OS updates may break it', 'App may stop on new Windows/Mac'],
            ['1 year', 'SSL certificates reject old TLS', 'Email/cloud features break'],
            ['2+ years', 'Docker images removed', 'Cannot rebuild or deploy'],
        ],
        [30, 55, 95]
    )

    # ─── SECTION 5: Migration Scope ───
    pdf.add_page()
    pdf.section_title('5', 'Migration Scope & Impact')
    pdf.sub_title('5.1 Code Changes Required')
    pdf.add_table(
        ['Category', 'Changes Needed', 'Automated?'],
        [
            ['Python 2 to 3 syntax', '~230 lines across 10 files', '80% via 2to3'],
            ['Django 1.11 to 4.2', '~150 lines across 5 files', 'Manual'],
            ['Model ForeignKey updates', '40+ model fields', 'Manual'],
            ['URL routing rewrite', '1 file (urls.py)', 'Manual'],
            ['Template tag updates', '30+ template files', 'Partial'],
            ['Library version upgrades', '20 libraries', 'Automated'],
        ],
        [55, 65, 60]
    )
    pdf.sub_title('5.2 What Stays the Same (No Impact)')
    pdf.add_table(
        ['Component', 'Status'],
        [
            ['Database schema (SQLite)', 'No changes - data preserved'],
            ['HTML/CSS templates', 'Minor changes - layout unchanged'],
            ['ECG algorithms (core math)', 'Same logic - only syntax changes'],
            ['Patient data', 'Fully preserved - migration handles it'],
            ['Report formats', 'Identical output - same PDF/print'],
        ],
        [60, 120]
    )

    # ─── SECTION 6: Benefits ───
    pdf.section_title('6', 'Benefits After Upgrade')
    pdf.add_table(
        ['Benefit', 'Impact'],
        [
            ['Security patches', 'Ongoing security updates for 3+ years'],
            ['2-3x faster', 'Python 3.12 is significantly faster'],
            ['Cross-platform', 'Windows, Mac, Linux, phone, tablet'],
            ['Modern testing', 'CI/CD, automated testing frameworks'],
            ['Easier maintenance', 'Current tools and documentation'],
            ['Better libraries', 'Latest medical/scientific libraries'],
            ['Compliance', 'Meet HIPAA, ISO 27001, FDA requirements'],
        ],
        [50, 130]
    )

    # ─── SECTION 7: Options ───
    pdf.add_page()
    pdf.section_title('7', 'Upgrade Options & Timeline')
    pdf.sub_title('Option A: Full Upgrade (Recommended)')
    pdf.add_table(
        ['Phase', 'Duration', 'Deliverable'],
        [
            ['Phase 1: Analysis & Planning', '1 week', 'Migration plan, test cases'],
            ['Phase 2: Core Migration', '2 weeks', 'Python 3.12 + Django 4.2'],
            ['Phase 3: Testing & Validation', '1 week', 'Side-by-side ECG comparison'],
            ['TOTAL', '4 weeks', 'Fully upgraded application'],
        ],
        [55, 30, 95]
    )
    pdf.sub_title('Option B: Docker-Only (Faster)')
    pdf.add_table(
        ['Phase', 'Duration', 'Deliverable'],
        [
            ['Phase 1: Backend Migration', '1 week', 'Python 3.12 + Django 4.2'],
            ['Phase 2: Testing', '1 week', 'Validated web application'],
            ['TOTAL', '2 weeks', 'Web-only application'],
        ],
        [55, 30, 95]
    )
    pdf.body_text('Trade-off: No standalone desktop .exe - clients access via browser.')
    pdf.sub_title('Option C: Stay on Python 2.7 (Short-term Only)')
    pdf.body_text(
        'Minimal cost now, but increasing technical debt and growing security/compatibility concerns. '
        'Viable only for 1-6 months.'
    )

    # ─── SECTION 8: Recommendation ───
    pdf.section_title('8', 'Recommendation')
    pdf.alert_box(
        'We strongly recommend Option A (Full Upgrade to Python 3.12 + Django 4.2 LTS). '
        'The 4-week investment eliminates 6 years of technical debt and ensures 5+ more years of support.',
        'blue'
    )
    pdf.body_text(
        '1. The application handles sensitive medical data - security compliance is non-negotiable.\n'
        '2. Patient data and report formats remain identical - no disruption to clinical workflows.\n'
        '3. Cross-platform support (phones, tablets) comes as a bonus.\n'
        '4. The upgraded application will be supportable for 5+ more years.'
    )

    # ─── SECTION 9: Data Safety ───
    pdf.section_title('9', 'Data Safety Guarantee')
    pdf.alert_box(
        'All patient data, reports, and configurations will be fully preserved during the upgrade.',
        'green'
    )
    pdf.add_table(
        ['Data Type', 'Protection Method'],
        [
            ['Patient records', 'SQLite database is version-independent'],
            ['ECG reports', 'Stored as files - not affected by code changes'],
            ['Hospital settings', 'Database records - migrated automatically'],
            ['Test history', 'Database records - migrated automatically'],
            ['User accounts', 'Django migration handles auth tables'],
        ],
        [60, 120]
    )

    # ─── SECTION 10: Next Steps ───
    pdf.section_title('10', 'Next Steps')
    pdf.add_table(
        ['Step', 'Action', 'Who'],
        [
            ['1', 'Review this document and confirm approach', 'Client'],
            ['2', 'Approve timeline (Option A or B)', 'Client'],
            ['3', 'Create migration branch, begin Phase 1', 'Dev Team'],
            ['4', 'Side-by-side ECG result validation', 'Dev + Clinical'],
            ['5', 'Sign-off and deploy', 'Client + Dev'],
        ],
        [15, 100, 65]
    )
    pdf.ln(15)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Document prepared by the Kodys Development Team for client review and approval.',
             align='C', new_x='LMARGIN', new_y='NEXT')

    # Save
    pdf.output(OUTPUT)
    size = os.path.getsize(OUTPUT)
    print(f"PDF generated successfully!")
    print(f"  Path: {OUTPUT}")
    print(f"  Size: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == '__main__':
    generate()
