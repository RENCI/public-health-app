import dash_mantine_components as dmc


def tooltip(children=[], label='', position='bottom-end'):
  return dmc.Tooltip(
    label=label,
    children=children,
    position=position,
    color='var(--mantine-color-dimmed)',
    withArrow=True,
    transitionProps=dict(
      transition='fade',
      duration=250,
      timingFunction='ease',
    ),
  )
