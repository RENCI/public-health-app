from enum import StrEnum
from typing import Iterable, Optional, Union
from dash.development.base_component import Component
import dash_mantine_components as dmc
from dash import html


class IconPlacement(StrEnum):
  left = 'left'
  right = 'right'


def _as_list(x):
  if x is None:
    return []
  return x if isinstance(x, (list, tuple)) else [x]


def toolbar_button(children, icon, icon_placement=IconPlacement.left, **kwargs):
  section_key = 'leftSection' if icon_placement == IconPlacement.left else 'rightSection'
  defaults = dict(variant='light', size='xs', **{section_key: icon})
  return dmc.Button(children or '', **{**defaults, **kwargs})


def toolbar(
  left: Optional[Union[Component, Iterable[Component]]] = None,
  right: Optional[Union[Component, Iterable[Component]]] = None,
  *,
  variant='soft',
  p='xs',
  mt=16,
  mb=24,
  gap='xs',
  justify='space-between',
  align='center',
  wrap=False,
  left_props=None,
  right_props=None,
  **kwargs,
):
  left = _as_list(left)
  right = _as_list(right)

  left_section = dmc.Flex(left, gap=gap, **(left_props or {})) if left else html.Div()
  right_section = dmc.Flex(right, gap=gap, **(right_props or {})) if right else html.Div()

  return dmc.Card(
    dmc.Flex(
      children=[left_section, right_section],
      justify=justify,
      align=align,
      wrap='wrap' if wrap else 'nowrap',
    ),
    variant=variant,
    p=p,
    mt=mt,
    mb=mb,
    **kwargs,
  )
