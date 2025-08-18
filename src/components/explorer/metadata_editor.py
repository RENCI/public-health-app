import dash_mantine_components as dmc

metadata_editor = dmc.Stack([
  dmc.TextInput(
    id='insight-title', 
    size='sm', 
    label='Title', 
    p=4,
  ),
  dmc.Textarea(
    id='insight-overview',
    size='sm',
    label='Overview',
    autosize=True,
    minRows=5,
  ),
], gap=8)
