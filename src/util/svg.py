import base64
import urllib.parse
from bs4 import BeautifulSoup


def clean_svg(svg_data_uri: str) -> str:
  """
  Cleans an SVG data URI by removing unnecessary elements.

  Args:
    svg_data_uri: A string representing the SVG as a data URI.

  Returns:
    A cleaned SVG data URI string.
  """
  print(svg_data_uri)
  if not svg_data_uri or not svg_data_uri.startswith('data:image/svg+xml'):
    return svg_data_uri

  header, encoded_data = svg_data_uri.split(',', 1)

  decoded_svg = urllib.parse.unquote(encoded_data)

  soup = BeautifulSoup(decoded_svg, 'html.parser')

  # remove all text, title, and defs elements
  for tag_name in ['text', 'title', 'defs']:
    for tag in soup.find_all(tag_name):
      tag.decompose()

  for element in soup.find('g', class_='bglayer'): element.decompose()
  for element in soup.find('g', class_='layer-below'): element.decompose()
  for element in soup.find('g', class_='polarlayer'): element.decompose()
  for element in soup.find('g', class_='smithlayer'): element.decompose()
  for element in soup.find('g', class_='ternarylayer'): element.decompose()
  for element in soup.find('g', class_='geolayer'): element.decompose()
  for element in soup.find('g', class_='funnelarealayer'): element.decompose()
  for element in soup.find('g', class_='pielayer'): element.decompose()
  for element in soup.find('g', class_='iciclelayer'): element.decompose()
  for element in soup.find('g', class_='treemaplayer'): element.decompose()
  for element in soup.find('g', class_='sunburstlayer'): element.decompose()
  for element in soup.find('g', class_='glimages'): element.decompose()

  # plotly specific: remove the top-level info layer which contains legends and titles
  for info_layer in soup.find_all('g', class_='infolayer'):
    info_layer.decompose()
  
  # remove style elements not needed for basic visuals
  for style in soup.find_all('style'):
    style.decompose()

  cleaned_svg_string = str(soup)

  encoded_cleaned_svg = urllib.parse.quote(cleaned_svg_string)

  return f'{header},{encoded_cleaned_svg}'

