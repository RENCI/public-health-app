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
    initial_state: bool = True,
  ) -> None:
    self.id = id

    self.store = CollapsibleCardStore(
      id=self.id, 
      initial_state=initial_state
    )

    self._layout = dmc.Card(
      [
        dmc.Group(
          children=[
            dmc.Text(title, fw=500),
            dmc.ActionIcon(
              DashIconify(icon='feather:chevron-up'),
              variant='transparent',
              id={'type': 'collapsible-card-toggle', 'index': self.id['index']},
            ),
          ],
          justify='space-between',
        ),
        dmc.Collapse(
          [
            dmc.Space(h=16),
            children,
          ],
          id={'type': 'collapse', 'index': self.id['index']},
          opened=initial_state,
        ),
        self.store.layout,
      ],
      variant='soft',
    )

  @property
  def layout(self):
    return self._layout
