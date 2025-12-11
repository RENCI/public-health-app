from typing import Any, Dict

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from src.components.collapsible_card.callbacks import CollapsibleCardCallbacks
from src.components.collapsible_card.store import CollapsibleCardStore


# ensure callbacks register only once
_callbacks = CollapsibleCardCallbacks()


class CollapsibleCard:
  def __init__(
    self,
    id: Dict[str, Any],
    title: str,
    children: Any,
    initial_open: bool = True,
  ) -> None:
    self.id = id

    self.store = CollapsibleCardStore(
      id=self.id, 
      initial_open=initial_open
    )

    self._layout = dmc.Card(
      [
        dmc.Button(
          dmc.Text(title, fw=500, style=dict(flex=1)),
          rightSection=DashIconify(icon='feather:chevron-up', id={'type': 'collapsible-card-toggle-icon', 'index': self.id['index']}),
          id={'type': 'collapsible-card-toggle', 'index': self.id['index']},
          justify='space-between',
          variant='transparent',
        ),
        dmc.Collapse(
          children=children,
          id={'type': 'collapse', 'index': self.id['index']},
          opened=initial_open,
          p='sm',
        ),
        self.store.layout,
      ],
      p=0,
      variant='soft',
    )

  @property
  def layout(self):
    return self._layout
