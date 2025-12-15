import dash_mantine_components as dmc

def actions_tray(actions: list = []):
  return dmc.Paper(
    dmc.Flex(
      actions,
      justify='flex-end',
      h='100%',
      direction=dict(base='row', sm='column'),
      gap='xs',
    ),
    p='xs',
    radius='sm',
    variant='outline',
  )

def insight_card(
  title: str,
  summary: str,
  href: str,
  image_url: str,
  actions=[],
):
  return dmc.Anchor(
    dmc.Card(
      dmc.Flex(
        [
          dmc.CardSection(
            dmc.Image(
              src=image_url,
              w=dict(base='100%', sm='300px'),
              radius='sm',
            ),
            p='md',
            pb=0,
          ),
          dmc.Stack(
            [
              dmc.Text(title, size='lg'),
              dmc.Text(summary, c='dimmed'),
            ],
            flex=1,
          ),
          actions_tray(actions) if len(actions) else None,
        ],
        direction=dict(base='column', sm='row'),
        gap='md',
      ),
      withBorder=True,
      className='emphasize-hover',
    ),
    href=href,
    underline=False,
  )
