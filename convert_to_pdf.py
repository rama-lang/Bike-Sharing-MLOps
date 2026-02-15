"""
Script to convert PROJECT_DOCUMENTATION.md to PDF
Requires: pip install markdown pdfkit
Also requires wkhtmltopdf installed on system
"""

import markdown
import pdfkit
from pathlib import Path

def convert_md_to_pdf():
    # Read markdown file
    md_file = Path("PROJECT_DOCUMENTATION.md")
    if not md_file.exists():
        print("❌ PROJECT_DOCUMENTATION.md not found!")
        return
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc']
    )
    
    # Add CSS styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 8px;
                margin-top: 30px;
            }}
            h3 {{
                color: #7f8c8d;
                margin-top: 25px;
            }}
            h4 {{
                color: #95a5a6;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            pre {{
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            pre code {{
                background-color: transparent;
                color: #ecf0f1;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 15px;
                color: #7f8c8d;
                font-style: italic;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .page-break {{
                page-break-after: always;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Save HTML temporarily
    html_file = Path("temp_documentation.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    
    print("✅ HTML file created: temp_documentation.html")
    
    # Convert to PDF
    try:
        pdf_file = "PROJECT_DOCUMENTATION.pdf"
        
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'print-media-type': None,
        }
        
        pdfkit.from_file(str(html_file), pdf_file, options=options)
        print(f"✅ PDF created successfully: {pdf_file}")
        
        # Clean up temporary HTML
        html_file.unlink()
        print("✅ Temporary HTML file removed")
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("\n📝 Alternative: You can open temp_documentation.html in a browser and print to PDF")
        print("   Or install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")

if __name__ == "__main__":
    print("🚀 Starting conversion...")
    convert_md_to_pdf()
