"""
Simple script to convert PROJECT_DOCUMENTATION.md to PDF using reportlab
Requires: pip install reportlab markdown
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
import re

def convert_md_to_pdf():
    # Read markdown file
    try:
        with open("PROJECT_DOCUMENTATION.md", 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print("❌ PROJECT_DOCUMENTATION.md not found!")
        return
    
    # Create PDF
    pdf_file = "PROJECT_DOCUMENTATION.pdf"
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#7f8c8d'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    h4_style = ParagraphStyle(
        'CustomH4',
        parent=styles['Heading4'],
        fontSize=12,
        textColor=HexColor('#95a5a6'),
        spaceAfter=6,
        spaceBefore=6
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=8,
        leftIndent=20,
        textColor=HexColor('#2c3e50'),
        backColor=HexColor('#f4f4f4')
    )
    
    # Build content
    story = []
    lines = md_content.split('\n')
    
    in_code_block = False
    code_buffer = []
    
    for line in lines:
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End of code block
                code_text = '\n'.join(code_buffer)
                if code_text.strip():
                    story.append(Preformatted(code_text, code_style))
                    story.append(Spacer(1, 0.2*inch))
                code_buffer = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            continue
        
        if in_code_block:
            code_buffer.append(line)
            continue
        
        # Skip empty lines
        if not line.strip():
            story.append(Spacer(1, 0.1*inch))
            continue
        
        # Handle headers
        if line.startswith('# '):
            text = line[2:].strip()
            if 'Bike Sharing MLOps Project' in text:
                story.append(Paragraph(text, title_style))
            else:
                story.append(PageBreak())
                story.append(Paragraph(text, h1_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, h2_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, h3_style))
        elif line.startswith('#### '):
            text = line[5:].strip()
            story.append(Paragraph(text, h4_style))
        elif line.startswith('---'):
            story.append(Spacer(1, 0.2*inch))
        elif line.startswith('- ') or line.startswith('* '):
            text = '• ' + line[2:].strip()
            story.append(Paragraph(text, body_style))
        else:
            # Regular paragraph
            # Escape special characters for reportlab
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Handle inline code
            text = re.sub(r'`([^`]+)`', r'<font face="Courier" color="#2c3e50">\1</font>', text)
            # Handle bold
            text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(text, body_style))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ PDF created successfully: {pdf_file}")
        print(f"📄 File size: {round(len(open(pdf_file, 'rb').read()) / 1024 / 1024, 2)} MB")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")

if __name__ == "__main__":
    print("🚀 Starting PDF conversion...")
    convert_md_to_pdf()
    print("✅ Done!")
