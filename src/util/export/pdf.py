import io
import os
import markdown
from playwright.sync_api import sync_playwright
from src.util.assets import asset_uri

LOGO_URI = asset_uri('images/covid19-smh-logo.png')

PDF_STYLES_PATH = os.path.join(os.path.dirname(__file__), 'pdf.css')

with open(PDF_STYLES_PATH, encoding='utf-8') as f:
  BASE_STYLES = f.read()

def wrap_template(body: str) -> str:
  return f"""
    <html>
      <head>
        <style>{BASE_STYLES}</style>
      </head>
      <body>
        {body}
      </body>
    </html>
  """


def md_to_html(md_text: str) -> str:
  return markdown.markdown(md_text, extensions=['extra', 'smarty'])


def html_to_pdf_bytes(html: str, header_html: str, footer_html: str) -> bytes:
  """Render HTML to PDF bytes using Playwright (Chromium)."""
  with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # set the content and wait for all resources (fonts/images) to load
    page.set_content(html, wait_until="networkidle")

    # generate the PDF (returns bytes)
    pdf_bytes = page.pdf(
      format='letter',
      print_background=True,
      display_header_footer=True,
      header_template=header_html,
      footer_template=footer_html,
      prefer_css_page_size=True,
    )

    browser.close()
    return pdf_bytes


def generate_round_pdf(round_dict):
  round_number = round_dict.get('round_number') or '18'
  
  summary_md = round_dict.get('report') or 'Report not found'
  summary_html = md_to_html(summary_md)
  
  insights = round_dict.get('insights') or []
  insights_list_html = '<ul>' + ''.join(f'<li>{insight["summary"]}</li>' for insight in insights) + '</ul>'

  insights_details_html = '<br />'.join(f"""
    <h2>{insight['title']}</h2>
    <figure>
      <img src="https://placehold.co/650x300?text=Visualization" style="width: 100%;">
      <figcaption>Figure {i+1}. Visualization caption</figcaption>
    </figure>
    <div>{md_to_html(insight['description'])}</div>
  """ for i, insight in enumerate(insights))

  header_html = f"""
    <header style="width: 100%; padding: 0.25in 1in 0 1in; height: 1in; background: azure; padding-bottom: 0.5rem;">
      <div style="height: 0.75in; display: flex; flex-direction: row; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #333; color: #333;">
        <div>
          <h1 style="font-size: 14pt; margin: 0;">Round {round_number}<br />Executive Summary Report</h1>
          <div style="font-size: 10pt; font-style: italic;">Round completed: June 4, 2025</div>
        </div>
        <img src="{LOGO_URI}" alt="SMH Logo" style="flex-basis: 300px; height: 53.668px; width: 300px; max-height: 53.668px; max-width: 300px;" />
      </div>
    </header>
  """

  main_html = f"""
    <main>
      {summary_html}
      <h2>Key Insights</h2>
      {insights_list_html}<br />
      {insights_details_html}<br />      
    </main>
  """

  footer_html = f"""
    <div style="width: 100%; padding: 0 1in; display: flex; justify-content: space-between; font-size: 8pt; color: #555;">
      <div><a href="https://covid19scenariomodelinghub.org/">https://covid19scenariomodelinghub.org/</a></div>
      <div>Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>
      <div>Round {round_number} Executive Summary Report</div>
    </div>
  """

  page_html = wrap_template(main_html)

  return html_to_pdf_bytes(html=page_html, header_html=header_html, footer_html=footer_html)


def generate_insight_pdf(insight):
  title = insight.get('title', '')
  summary = insight.get('summary') or ''
  description_md = insight.get('description') or 'Details not found'
  description_html = md_to_html(description_md)
  controls = insight.get('controls', {})
  round_number = controls.get('round', '18')

  header_html = f"""
    <header style="width: 100%; padding: 0 1in; height: 1in; background: azure; padding-bottom: 0.5rem;">
      <div style="height: 0.75in; display: flex; flex-direction: row; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #333; color: #333;">
        <div>
          <h1 style="font-size: 14pt; margin: 0;">Round {round_number} Insight Report:<br />{title}</h1>
          <div style="font-size: 10pt; font-style: italic;">Round completed: June 4, 2025</div>
        </div>
        <img src="{LOGO_URI}" alt="SMH Logo" style="flex-basis: 300px; height: 53.668px; width: 300px; max-height: 53.668px; max-width: 300px;" />
      </div>
    </header>
  """

  main_html = f"""
    <main>
      {summary}<br />
      {description_html}<br />
      <img src="https://placehold.co/650x300?text=Visualization" style="width: 100%;">
    </main>
  """

  footer_html = f"""
    <div style="width: 100%; padding: 0 1in; display: flex; justify-content: space-between; font-size: 8pt; color: #555;">
      <div><a href="https://covid19scenariomodelinghub.org/">https://covid19scenariomodelinghub.org/</a></div>
      <div>Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>
      <div>Round {round_number} Insight Report</div>
    </div>
  """

  page_html = wrap_template(main_html)

  return html_to_pdf_bytes(html=page_html, header_html=header_html, footer_html=footer_html)
