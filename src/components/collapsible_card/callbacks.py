from dash import Input, Output, State, callback, ALL, ctx

from src.components.collapsible_card.store import CollapsibleCardStore


class CollapsibleCardCallbacks:
  def __init__(self) -> None:
    # only register callbacks once
    self._setup_callbacks()

  def _setup_callbacks(self) -> None:
    # toggle open/closed
    @callback(
      Output(CollapsibleCardStore.get_id(match_all=True), 'data'),
      Input({'type': 'collapsible-card-toggle', 'index': ALL}, 'n_clicks'),
      State(CollapsibleCardStore.get_id(match_all=True), 'data'),
    )
    def toggle_collapsible_card(_clicks, states):
      tid = ctx.triggered_id
      if not tid:
        return states

      for state in states:
        if state['id']['index'] == tid['index']:
          state['isOpen'] = not state['isOpen']

      return states

    # each card updates its own Collapse.is_open
    @callback(
      Output({'type': 'collapse', 'index': ALL}, 'opened'),
      Output({'type': 'collapsible-card-toggle-icon', 'index': ALL}, 'style'),
      Input(CollapsibleCardStore.get_id(match_all=True), 'data'),
    )
    def update_visibility(states):
      # list of booleans for Collapse.opened
      opened_states = [state['isOpen'] for state in states]

      # list of styles applied to each chevron icon
      # rotate when open
      chevron_styles = [
        {
          'transform': 'rotate(0deg)' if state['isOpen'] else 'rotate(180deg)',
          'transition': 'transform 150ms ease',
        }
        for state in states
      ]

      return opened_states, chevron_styles
