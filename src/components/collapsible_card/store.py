import dash
from dash import dcc
from typing import Dict, Any


class CollapsibleCardStore:
  STORE_TYPE = 'collapsible-card-store'

  def __init__(self, id: Dict[str, Any], initial_open: bool = True):
    self.id = {'type': self.STORE_TYPE, 'index': id['index']}
    self.initial_open = initial_open

  @staticmethod
  def get_id(match_all=False):
    if match_all:
      return {'type': CollapsibleCardStore.STORE_TYPE, 'index': dash.ALL}
    return {'type': CollapsibleCardStore.STORE_TYPE, 'index': dash.MATCH}

  @property
  def layout(self):
    return dcc.Store(
      id=self.id,
      data={
        'id': self.id,
        'isOpen': self.initial_open,
      },
    )
