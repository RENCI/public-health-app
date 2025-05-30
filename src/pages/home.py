import dash
from dash import dcc, html
import dash_mantine_components as dmc
from src.components.controls import controls_debugger

dummy_content = dcc.Markdown('''
## Lorem Ipsum Dolor Sit Amet

### Consectetur Adipiscing Elit

Lorem ipsum dolor sit amet, **consectetur adipiscing elit**. _Vestibulum vel sapien euismod_, tincidunt ligula non, scelerisque nulla. 

> "Nulla facilisi. Sed fermentum quam vel erat vehicula, at sagittis nisi varius."

#### Pellentesque Habitant

- **Aenean** et nisl nec libero fermentum pharetra.  
- **Morbi** convallis, justo eget luctus bibendum, nunc felis sodales velit.  
- **Suspendisse** potenti.
''')

layout = dmc.Container(
  [
    html.H1('Welcome'),
    html.Hr(),
    dummy_content,
    controls_debugger,
  ],
  fluid=True
)

dash.register_page('home', layout=layout, path='/')
