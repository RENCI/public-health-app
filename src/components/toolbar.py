import dash_mantine_components as dmc
from dash import html


def toolbar_button(children, icon, **kwargs):
  defaults = dict(
    leftSection=icon,
    variant='light',
    size='xs',
  )

  # remove conflicting keys from kwargs so defaults win, unless overridden
  for key in list(defaults.keys()):
    if key in kwargs:
      pass

  # merge defaults with incoming overrides
  final_props = {**defaults, **kwargs}

  return dmc.Button(children, **final_props)


def toolbar(
  left=None,
  right=None,
  *,
  variant='soft',
  p='xs',
  mt=16,
  mb=24,
  gap='xs',
  justify='space-between',
  align='center',
):
  '''
  Toolbar component.

  Parameters
  ----------
  left : Component | list[Component] | None
    Elements aligned to the left side (e.g., Back button).
  right : Component | list[Component] | None
    Elements aligned to the right side (e.g., Download, Explorer buttons).
  variant : str, default='soft'
    Mantine Card variant.
  p : str or int, default='xs'
    Card padding.
  mt : str or int | None
    Top margin.
  mb : str or int, default=24
    Bottom margin.
  gap : str, default='xs'
    Gap between elements in left/right groups.
  justify : str, default='space-between'
    Flex item justification.
  align : str, default='center'
    Flex item alignment.

  Returns
  -------
  dmc.Card
  '''

  # normalize left and right to lists
  if left is None:
    left = []
  elif not isinstance(left, (list, tuple)):
    left = [left]

  if right is None:
    right = []
  elif not isinstance(right, (list, tuple)):
    right = [right]

  # inner layout
  return dmc.Card(
    dmc.Flex(
      children=[
        dmc.Flex(left, gap=gap) if left else html.Div(),
        dmc.Flex(right, gap=gap) if right else html.Div(),
      ],
      justify=justify,
      align=align,
    ),
    variant=variant,
    p=p,
    mt=mt,
    mb=mb,
  )
