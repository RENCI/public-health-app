from dash import dcc, html, register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from ..data.insights import insights

register_page(__name__, path='/')

def create_insight_button(item):
  graphic = dmc.Image(
    src=item['image_url'],
    radius='sm',
    style=dict(width='125px', height='125px', objectFit='cover')
  )

  title = dmc.Text(item['title'], size='lg', style=dict(whiteSpace='normal', textAlign='left'))

  description = dmc.Text(item['overview'], size='sm', style=dict(whiteSpace='normal', textAlign='left'))

  button = dmc.Anchor(
    [
      'View',
      dmc.Space(w=8),
      DashIconify(icon='feather:arrow-right', width=20),
    ],
    href=f"/viewer/{item['id']}",
    style=dict(
      textDecoration='none',
      padding='1rem',
      backgroundColor='color-mix(in hsl, var(--mantine-color-anchor), transparent 90%)',
      display='flex',
      justifyContent='center',
      alignItems='center',
      minHeight='100%',
      color='var(--mantine-color-anchor)',
    )
  )

  return dmc.Paper(
    [
      graphic,
      dmc.Stack(
        [title, description],
        align='flex-start',
        style=dict(flex=1),
      ),
      button,
    ],
    style=dict(
      display='flex', 
      gap='1rem', 
      justifyContent='flex-start', 
      alignItems='stretch', 
      minHeight='150px',
      padding='1rem',
      border='1px solid var(--mantine-color-disabled-border)'
    ),
  )

insight_buttons = [create_insight_button(item) for item in insights]

layout = dmc.Container(
  [
    dmc.Title('Select an Insight', order=1, my=24, style=dict(textAlign='center')),
    dmc.Stack(
      insight_buttons, 
      gap='md', 
      style=dict(width='100%', margin='auto', maxWidth='800px'),
    ),
  ],
  fluid=True
)
