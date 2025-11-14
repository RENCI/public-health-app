def replace_opacity(color: str, opacity: float) -> str:
  """Replace the opacity of a color. Color must be in the format 'rgba(r,g,b,1)'."""
  if not color.startswith('rgba('):
    raise ValueError('Color must be in the format "rgba(r,g,b,opacity)".')
  prefix_with_r, g, b, _ = color.split(',')
  return f'{prefix_with_r},{g},{b},{opacity})'
