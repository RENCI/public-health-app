import os
import markdown
from weasyprint import HTML

from src.util.assets import asset_uri
from src.util.data import load_rounds

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
    <body>{body}</body>
  </html>
  """


def md_to_html(md_text: str) -> str:
  return markdown.markdown(md_text, extensions=['extra', 'smarty'])


def generate_round_pdf(round_dict):
  round_number = round_dict.get('round_number') or '18'
  date = round_dict.get('date') or '...'

  summary_md = round_dict.get('report') or 'Report not found'
  summary_html = md_to_html(summary_md)

  insights = round_dict.get('insights') or []
  insights_list_html = (
    '<ul>' + ''.join(f'<li>{insight["summary"]}</li>' for insight in insights) + '</ul>'
  )

  insights_details_html = '<br />'.join(
    f"""
    <h2>{insight['title']}</h2>
    <figure>
      <img src="{insight['image_url']}" style="width: 100%;">
      <figcaption>Figure {i + 1}. Visualization caption</figcaption>
    </figure>
    <div>{md_to_html(insight['description'])}</div>
  """
    for i, insight in enumerate(insights)
  )

  body = f"""
    <header>
      <div class="header-title">
        <h1 class="title">Round {round_number}<br />Executive Summary Report</h1>
        <div class="subtitle">Round completed: {date}</div>
      </div>
      <img src="{LOGO_URI}" alt="SMH Logo" class="header-smh-logo" />
    </header>
    <main>
      {summary_html}

      <h2>Key Insights</h2>
      {insights_list_html}

      {insights_details_html}
      
    </main>
  """

  pdf_html = wrap_template(body)
  pdf_bytes = HTML(string=pdf_html).write_pdf()

  return pdf_bytes


def generate_insight_pdf(insight):
  title = insight.get('title', '')
  image_url = insight.get('image_url')
  summary = insight.get('summary') or ''
  description_md = insight.get('description') or 'Details not found'
  description_html = md_to_html(description_md)
  controls = insight.get('controls', {})
  round_number = controls.get('round', '18')

  rounds = load_rounds()
  this_round = rounds.get(round_number)
  round_date = this_round.get('date', '...')

  body = f"""
    <header>
      <div class="header-title">
        <h1 class="title">Round {round_number}<br />Insight Report:<br />{title}</h1>
        <div class="subtitle">Round completed: {round_date}</div>
      </div>
      <img src="{LOGO_URI}" alt="SMH Logo" class="header-smh-logo" />
    </header>
    <main>
      {summary}
      <br />

      {description_html}

      <img src="{image_url}" style="width: 100%;">
      
    </main>
  """

  pdf_html = wrap_template(body)
  pdf_bytes = HTML(string=pdf_html).write_pdf()

  return pdf_bytes
